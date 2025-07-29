import base64
import io
import logging
import os
from typing import Union

from PIL import Image
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from .prompt.prompt import Prompt
from .services.coder import Coder
from .trae.trae_env import TraeEnv
from .utils.image import image_to_base64, url_to_base64, validate_base64_image
from .utils.ocr import OCRError, extract_text_from_image
from .vision.anthropic import AnthropicVision
from .vision.cloudflare import CloudflareWorkersAI
from .vision.openai import OpenAIVision

# Load environment variables
load_dotenv()

# Configure encoding, defaulting to UTF-8
DEFAULT_ENCODING = "utf-8"
ENCODING = os.getenv("MCP_OUTPUT_ENCODING", DEFAULT_ENCODING)

# 默认代理配置
DEFAULT_HTTP_PROXY = "http://10.2.48.171:7888"

# Configure logging to file
log_file_path = os.path.join(os.path.dirname(__file__), "mcp_server.log")
print(f"log_file_path:{log_file_path}")
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "ERROR"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename=log_file_path,
    filemode="a",  # Append to log file
)
logger = logging.getLogger(__name__)

logger.info(f"Using encoding: {ENCODING}")


def sanitize_output(text: str) -> str:
    """Sanitize output string to replace problematic characters."""
    if text is None:
        return ""  # Return empty string for None
    try:
        return text.encode(ENCODING, "replace").decode(ENCODING)
    except Exception as e:
        logger.error(f"Error during sanitization: {str(e)}", exc_info=True)
        return text  # Return original text if sanitization fails


# Create MCP server
mcp = FastMCP(
    "szetop-trae-dev",
    description="易图代码生成服务：支持识别设计图或 UI 效果图中的参数与字段，可用于生成代码提示词（Prompt）或直接提取界面内容。",
)


# Initialize vision clients
def get_vision_client() -> Union[AnthropicVision, OpenAIVision, CloudflareWorkersAI]:
    """Get the configured vision client based on environment settings."""
    provider = os.getenv("VISION_PROVIDER", "anthropic").lower()

    try:
        if provider == "anthropic":
            return AnthropicVision()
        elif provider == "openai":
            return OpenAIVision()
        elif provider == "cloudflare":
            return CloudflareWorkersAI()
        else:
            raise ValueError(f"Invalid vision provider: {provider}")
    except Exception as e:
        # Try fallback provider if configured
        fallback = os.getenv("FALLBACK_PROVIDER")
        if fallback and fallback.lower() != provider:
            logger.warning(
                f"Primary provider failed: {str(e)}. Trying fallback: {fallback}"
            )
            if fallback.lower() == "anthropic":
                return AnthropicVision()
            elif fallback.lower() == "openai":
                return OpenAIVision()
            elif fallback.lower() == "cloudflare":
                return CloudflareWorkersAI()
        raise


async def process_image_with_ocr(image_data: str) -> str:
    """Process image with both vision AI and OCR.

    Args:
        image_data: Base64 encoded image data

    Returns:
        str: Combined description from vision AI and OCR
    """
    # Get vision AI description
    client = get_vision_client()

    # Handle both sync (Anthropic) and async (OpenAI, Cloudflare) clients
    image_prompt = Prompt.get_describe_image_prompt()
    if isinstance(client, (OpenAIVision, CloudflareWorkersAI)):
        description = await client.describe_image(image_data, image_prompt)
    else:
        description = client.describe_image(image_data, image_prompt)

    # Check for empty or default response
    if not description or description == "No description available.":
        raise ValueError("Vision API returned empty or default response")

    # Handle OCR if enabled
    ocr_enabled = os.getenv("ENABLE_OCR", "false").lower() == "true"
    if ocr_enabled:
        try:
            # Convert base64 to PIL Image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Extract text with OCR required flag
            if ocr_text := extract_text_from_image(image, ocr_required=True):
                description += (
                    f"\n\nAdditionally, this is the output of tesseract-ocr: {ocr_text}"
                )
        except OCRError as e:
            # Propagate OCR errors when OCR is enabled
            logger.error(f"OCR processing failed: {str(e)}")
            raise ValueError(f"OCR Error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during OCR: {str(e)}")
            raise

    return sanitize_output(description)


# @mcp.tool()
async def describe_image(
        image: str
) -> str:
    """
    识别并描述来自 Base64 编码图像的数据内容，适用于用户通过聊天窗口上传的图片。

    Best for: 当前对话中直接上传的图片（无公共 URL 时使用）。
    Not suitable for: 本地文件路径或公网链接图像，请使用 describe_image_from_file 工具。

    Args:
        image (str): 图像的 Base64 编码字符串（如 data:image/png;base64,...）

    Returns:
        str: 图像内容的详细自然语言描述，适用于提取页面字段、UI 布局、结构分析等任务。
    """
    try:
        logger.debug(f"Image data length: {len(image)}")

        # Validate image data
        if not validate_base64_image(image):
            raise ValueError("Invalid base64 image data")

        result = await process_image_with_ocr(image)
        if not result:
            raise ValueError("Received empty response from processing")

        logger.info("Successfully processed image")
        return sanitize_output(result)
    except ValueError as e:
        logger.error(f"Input error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error describing image: {str(e)}", exc_info=True)
        raise


# @mcp.tool()
async def describe_image_from_file(
        filepath: str
) -> str:
    """
    识别本地设计图或 UI 效果图中的关键信息，包括接口参数和响应字段。

    Best for: 本地文件系统中存储的图片（如 UI 设计图、页面原型图、接口草图等）。
    Not suitable for: 直接在对话中上传的图片或网络 URL，请使用 describe_image 工具。

    Args:
        filepath (str): 图像文件的绝对路径，例如：/home/user/images/example.png 或 C:\\Users\\user\\Desktop\\ui.png

    Returns:
        str: 图像中提取的详细内容描述，包含推测的接口请求参数、响应字段及其含义，可用于自动生成 DTO/VO 类或接口草图。
    """
    try:
        logger.info(f"Processing image file: {filepath}")

        # Convert image to base64
        image_data, mime_type = image_to_base64(filepath)
        logger.info(f"Successfully converted image to base64. MIME type: {mime_type}")
        logger.debug(f"Base64 data length: {len(image_data)}")

        # Use describe_image tool
        result = await describe_image(image=image_data)

        if not result:
            raise ValueError("Received empty response from processing")

        return sanitize_output(result)
    except FileNotFoundError:
        logger.error(f"Image file not found: {filepath}")
        raise
    except ValueError as e:
        logger.error(f"Input error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing image file: {str(e)}", exc_info=True)
        raise


# @mcp.tool()
async def describe_image_from_url(
        url: str
) -> str:
    """
    从公网图片 URL 中识别图像内容，适用于 UI 设计图、接口草图等，提取接口参数与响应字段信息。

    Best for: 可公开访问的图像 URL（如部署在 OSS、图床、CDN 上的设计图）。
    Not suitable for: 本地文件或用户直接上传到对话中的图片，请使用 describe_image_from_file 或 describe_image。

    Args:
        url (str): 图像的公网直链地址，需确保该链接可被服务器访问，例如 https://example.com/images/mock.png

    Returns:
        str: 对图像的结构化描述，包含推测的接口字段、参数、页面元素等信息，适用于自动生成 DTO/VO 类或接口设计草稿。
    """
    try:
        logger.info(f"Processing image from URL: {url}")

        # Fetch image from URL and convert to base64
        image_data, mime_type = url_to_base64(url)
        logger.info(f"Successfully fetched image from URL. MIME type: {mime_type}")
        logger.debug(f"Base64 data length: {len(image_data)}")

        # Use describe_image tool
        result = await describe_image(image=image_data)

        if not result:
            raise ValueError("Received empty response from processing")

        return sanitize_output(result)
    except ValueError as e:
        logger.error(f"Input error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error processing image from URL: {str(e)}", exc_info=True)
        raise


coder = Coder(api_key="app-pYnTFIO9NGt7xFaa4q4Ow4Zk", api_base_url="http://10.2.54.19/v1")


@mcp.tool()
async def generate_api_code_prompt(project_folder: str, image_path: list[str], entity_paths: list[str],
                                   business_logic: str = None) -> str:
    """
    根据 UI 设计图或原型图和实体类生成构建列表页\新增编辑页\详情页所需的提示词（prompt），用于自动生成 Java 代码。

    Args:
       project_folder (str): 项目工程根目录的绝对路径，例如：
         C:\\Users\\user\\project

       image_path (str): UI 图片文件的本地绝对路径，可能多个，例如：
         C:\\Users\\user\\Desktop\\ui.png

       entity_paths (list[str]): 实体类的本地绝对路径，可能多个，例如：
         C:\\Users\\user\\Desktop\\entity\\User.java

       business_logic (str, optional): 业务逻辑描述，从用户输入需求中提取，辅助生成更准确的提示词。

    Returns:
        str: 用于生成 Controller、Service、DTO、VO、Mapper 等 Java 代码的自然语言提示词。
    """

    # 设置Trae的整体规则
    TraeEnv.set_rules(project_folder)

    # 判断是否多张图片
    if len(image_path) > 1:
        return "暂不支持多张图片，后续开放，请上传一张图片"

    if entity_paths is None or len(entity_paths) == 0:
        raise TypeError("请传入对应实体类")

    try:
        return coder.get_code_entire_prompt(image_path, entity_paths, business_logic)
    except Exception as e:
        logger.error(f"Error processing image file: {str(e)}", exc_info=True)
        return "运行异常，请终止后面的逻辑"


# @mcp.tool()
async def generate_api_code_prompt_test(project_folder: str, image_path: str, entity_paths: list[str],
                                        business_logic: str = None) -> str:
    """
      根据 UI 设计图和实体类生成构建接口代码所需的提示词（prompt），用于自动生成 Java 代码。

    Args:
        project_folder (str): 项目工程根目录的绝对路径，例如：
            - Linux/macOS: /home/user/project
            - Windows: C:\\Users\\user\\project

        image_path (str): UI 图像文件的本地绝对路径，例如：
            - Linux/macOS: /home/user/images/example.png
            - Windows: C:\\Users\\user\\Desktop\\ui.png

        entity_paths (list[str]): 实体类的本地绝对路径，可能多个，例如：
            - Linux/macOS: /home/user/images/entity/User.java
            - Windows: C:\\Users\\user\\Desktop\\entity\\User.java

        business_logic (str, optional): 业务逻辑描述，从用户输入需求中提取，辅助生成更准确的提示词。

    Returns:
        str: 用于生成 Controller、Service、DTO、VO、Mapper 等 Java 代码的自然语言提示词。
    """

    # 设置Trae的整体规则
    TraeEnv.set_rules(project_folder)

    if entity_paths is None or len(entity_paths) == 0:
        raise TypeError("请选择对应实体类")

    # 使用AI识别图片内容
    image_desc = await describe_image_from_file(image_path)
    logger.info(f"Image description: {image_desc}")

    # 生成提示词并返回
    try:
        return Prompt.generate_code_list_prompt(entity_paths, image_desc, business_logic)
    except Exception as e:
        logger.error(f"Input error: {str(e)}")
        return str(e)


# @mcp.tool()
async def user_login(user_name: str, user_pass: dict) -> str:
    """
    用户登录，获取session_id，调用其他接口

    Args:
       user_name (str): 用户账号，询问用户获得，例如：请输入你的账号和密码登录工具系统

       user_pass (dict): 用户密码，询问用户获得，例如：请输入你的账号和密码登录工具系统
    Returns:
        str: 返回用户登录成功的session_id，以调用其他接口。
    """
    if user_name is None:
        raise TypeError("请输入你的账号")

    if user_pass is None:
        raise TypeError("请输入你的密码")

    return "login_success_123"


def main():
    """Entry point for the MCP server."""
    print("[DEBUG] MCP Server starting...")
    # 检查环境
    TraeEnv.check_env(http_proxy=os.getenv("HTTP_PROXY", DEFAULT_HTTP_PROXY))
    print("[DEBUG] MCP Server running...")
    mcp.run()


if __name__ == "__main__":
    main()
