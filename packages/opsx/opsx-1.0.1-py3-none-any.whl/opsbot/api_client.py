# src/api_client.py

import sys
import click
from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError
from .config import OpsBotConfig

class ApiClient:
    def __init__(self, config: OpsBotConfig):
        self.config = config
        self.client = None
        if not config.openai_api_key or "YOUR_OPENAI_API_KEY_HERE" in config.openai_api_key:
            click.echo(click.style("错误: OpenAI API Key 未在 .ops 文件中配置。", fg='red'), err=True)
            click.echo(click.style("请运行 'opsbot init' 并编辑 .ops 文件。", fg='yellow'), err=True)
            sys.exit(1)
        try:
            self.client = OpenAI(api_key=self.config.openai_api_key, base_url=self.config.openai_base_url)
        except Exception as e:
            click.echo(click.style(f"初始化 OpenAI 客户端时出错: {e}", fg='red'), err=True)
            sys.exit(1)

    def get_completion(self, messages: list) -> str:
        if not self.client: return "OpenAI client is not initialized."
        full_response = ""
        try:
            stream = self.client.chat.completions.create(model=self.config.openai_default_model, messages=messages, stream=True)
            click.echo(click.style("Assistant: ", fg='blue'), nl=False)
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    click.echo(content, nl=False)
                    full_response += content
            click.echo() # Newline
            return full_response
        except AuthenticationError:
            click.echo(click.style("\nOpenAI API Key 认证失败，请检查你的 Key 是否正确。", fg='red'), err=True)
        except RateLimitError:
            click.echo(click.style("\n已达到 OpenAI API 的速率限制，请稍后再试。", fg='red'), err=True)
        except APIConnectionError as e:
            click.echo(click.style(f"\n无法连接到 OpenAI API: {e}", fg='red'), err=True)
        except Exception as e:
            click.echo(click.style(f"\n与 API 交互时发生未知错误: {e}", fg='red'), err=True)
        return ""