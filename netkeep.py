import json
import os
import time
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

# 处理配置文件
def process_config_file():
    """从分段的配置文件生成单行JSON格式的配置文件"""
    config_path = 'config.json'
    env_path = '.env'

    # 检查是否存在config.json文件
    if os.path.exists(config_path):
        try:
            # 读取分段的JSON配置
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # 将配置写入.env文件
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.read()

            # 查找FREECLOUD_ACCOUNTS行并替换
            import re
            pattern = r'FREECLOUD_ACCOUNTS=\[.*?\]'
            compact_json = json.dumps(config_data, ensure_ascii=False, separators=(',', ':'))
            new_env_content = re.sub(pattern, f'FREECLOUD_ACCOUNTS={compact_json}', env_content, flags=re.DOTALL)

            # 写入新的.env文件
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(new_env_content)

            print("已从config.json生成配置")
        except Exception as e:
            print(f"处理配置文件时出错: {str(e)}")

# 处理配置文件并加载.env文件
process_config_file()
load_dotenv(override=True)  # 使用override=True强制重新加载.env文件


def send_telegram_message(message):
    """发送Telegram通知，如果配置缺失则只打印消息"""
    # 本地调试模式下，只打印消息，不发送Telegram通知
    debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'

    # 检查Telegram配置是否存在
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    # 如果是调试模式或Telegram配置缺失，只打印消息
    if debug_mode or not (bot_token and chat_id):
        if debug_mode:
            print("调试模式: 跳过Telegram通知")
        elif not (bot_token and chat_id):
            print("Telegram配置缺失: 跳过Telegram通知")

        # 无论是哪种情况，都打印消息内容
        print(f"消息内容:\n{message}")
        return {"ok": True, "result": {"message_id": 0}}

    # 正常模式且Telegram配置存在，发送通知
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"发送Telegram通知失败: {str(e)}")
        print(f"消息内容:\n{message}")
        return {"ok": False, "error": str(e)}

def login_and_get_cookie(account, browser, max_retries=5):  # 增加重试次数
    # 检查是否需要获取Cookie
    # 如果没有renewApi字段，默认不需要获取Cookie
    need_cookie = account.get('needCookie', 'renewApi' in account)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
        extra_http_headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Upgrade-Insecure-Requests': '1'
        }
    )
    page = context.new_page()

    for attempt in range(max_retries):
        try:
            login_url = f"{account['site']}{account['loginApi']}"
            print(f"尝试 {attempt + 1}/{max_retries}: 导航到 {login_url} 登录 {account['username']}")
            # 增加超时时间到120秒
            page.goto(login_url, wait_until='load', timeout=120000)

            # 填写表单
            page.fill('input[name="username"]', account['username'])
            page.fill('input[name="password"]', account['password'])
            page.evaluate('() => { const remember = document.querySelector(\'input[name="remember"]\'); if (remember) remember.checked = true; }')

            # 提交登录
            print(f"提交登录表单...")
            page.click('button[type="submit"]')
            page.wait_for_load_state('load', timeout=120000)  # 增加超时时间

            # 等待一段时间，确保登录完成
            print(f"等待3秒，确保登录完成...")
            time.sleep(3)

            # 只有需要获取Cookie时才访问 /server/lxc 建立会话
            if need_cookie:
                print(f"导航到 {account['site']}/server/lxc 页面...")
                page.goto(f"{account['site']}/server/lxc", wait_until='load', timeout=120000)  # 增加超时时间
            else:
                print(f"不需要获取Cookie，跳过导航到 {account['site']}/server/lxc 页面")

            # 如果需要获取Cookie
            if need_cookie:
                # 获取 Cookie
                cookies = context.cookies()
                sw110xy_cookie = next((c for c in cookies if c['name'] == 'sw110xy'), None)
                cf_clearance_cookie = next((c for c in cookies if c['name'] == 'cf_clearance'), None)

                if not sw110xy_cookie:
                    raise Exception('sw110xy cookie not found')

                cookie_value = f"{sw110xy_cookie['name']}={sw110xy_cookie['value']};1"
                print(f"账号 {account['username']} 登录成功，Cookie: {cookie_value}")

                return context, cookie_value, cf_clearance_cookie
            else:
                # 不需要获取Cookie，只需登录
                print(f"账号 {account['username']} 登录成功，不需要获取Cookie")
                return context, None, None
        except PlaywrightTimeoutError as e:
            print(f"账号 {account['username']} 登录尝试 {attempt + 1} 失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
        except Exception as e:
            print(f"账号 {account['username']} 登录失败: {str(e)}")
            raise
        finally:
            page.close()

def renew_vps(account, context, cookie, cf_clearance_cookie=None, max_retries=3):
    page = context.new_page()

    try:
        for attempt in range(max_retries):
            try:
                # 导航到续期页面
                print(f"尝试 {attempt + 1}/{max_retries}: 导航到 {account['site']}/server/lxc 页面...")
                page.goto(f"{account['site']}/server/lxc", wait_until='load', timeout=120000)  # 增加超时时间

                # 等待一段时间，确保页面加载完成
                print(f"等待3秒，确保页面加载完成...")
                time.sleep(3)

                # 准备续期请求
                renew_url = f"{account['site']}{account['renewApi']}"
                print(f"账号 {account['username']} 的续期URL: {renew_url}")

                # 使用Playwright的内置请求功能
                print(f"正在为账号 {account['username']} 提交续期请求...")

                # 设置请求头
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest'
                }

                # 设置请求体
                data = {
                    'month': '1',
                    'coupon_id': '0',
                    'submit': '1'
                }

                # 发送POST请求
                response = page.request.post(
                    renew_url,
                    headers=headers,
                    form=data
                )

                # 获取响应
                status = response.status
                response_text = response.text()

                print(f"账号 {account['username']} 续期响应状态码: {status}")
                print(f"账号 {account['username']} 续期响应内容: {response_text}")

                # 如果请求成功，返回响应文本
                if status == 200:
                    return response_text
                else:
                    print(f"续期请求返回非200状态码: {status}")
                    if attempt < max_retries - 1:
                        print(f"等待5秒后重试...")
                        time.sleep(5)
                        continue
                    else:
                        raise Exception(f"续期请求失败，状态码: {status}")
            except Exception as e:
                print(f"续期尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待5秒后重试...")
                    time.sleep(5)
                    continue
                raise
        # 如果所有尝试都失败，抛出异常
        raise Exception(f"所有 {max_retries} 次续期尝试都失败")
    finally:
        page.close()

def main():
    # 从环境变量加载账号信息
    freecloud_accounts_env = os.environ.get('FREECLOUD_ACCOUNTS', '[]')
    accounts = json.loads(freecloud_accounts_env)

    # 打印读取到的账号信息
    print("\n读取到的账号信息:")
    for i, account in enumerate(accounts):
        # 获取网站类型信息（从域名的结尾前一段获取）
        try:
            # 提取域名部分
            domain = account['site'].split('//')[1]
            # 分割域名并获取倒数第二段
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                site_name = domain_parts[-2]  # 获取倒数第二段
            else:
                site_name = domain
        except:
            site_name = account['site']

        need_renew = 'renewApi' in account and account['renewApi']
        # 如果没有renewApi字段，默认不需要获取Cookie
        need_cookie = account.get('needCookie', need_renew)

        if need_renew:
            print(f"账号 {i+1}: {account['username']} ({site_name}), 需要续期, 续期API: {account['renewApi']}")
        else:
            print(f"账号 {i+1}: {account['username']} ({site_name}), 仅登录, 不需要续期")

    # 本地调试模式，允许手动输入账号信息
    debug_mode = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    if debug_mode and not accounts:
        # 如果环境变量中没有账号信息，则提示用户手动输入
        print("环境变量中未找到账号信息，请手动输入：")
        accounts = []
        num_accounts = int(input("请输入要添加的账号数量: "))

        for i in range(num_accounts):
            # 输入基本信息
            site = input(f"请输入账号 {i+1} 的网站地址 (默认: https://freecloud.ltd): ").strip()
            if not site:
                site = "https://freecloud.ltd"

            login_api = input(f"请输入账号 {i+1} 的登录API (默认: /login): ").strip()
            if not login_api:
                login_api = "/login"

            username = input(f"请输入账号 {i+1} 的用户名: ")
            password = input(f"请输入账号 {i+1} 的密码: ")

            account = {
                "site": site,
                "loginApi": login_api,
                "username": username,
                "password": password
            }

            # 询问是否需要获取Cookie (只有在需要续期时才询问)
            # 这部分是可选的，因为我们已经根据renewApi自动决定是否需要获取Cookie
            # 但保留这个选项，以便用户可以手动覆盖默认行为

            # 询问是否需要续期
            need_renew = input(f"账号 {i+1} 是否需要续期? (y/n, 默认: n): ").lower().strip()
            if need_renew == 'y' or need_renew == 'yes':
                renew_api = input(f"请输入账号 {i+1} 的续期API (例如: /server/detail/1707/renew): ")
                if renew_api:
                    account["renewApi"] = renew_api

            accounts.append(account)

    if not accounts:
        print("FREECLOUD_ACCOUNTS 环境变量中未配置任何账号")
        send_telegram_message("Freecloud 续期失败: 没有配置任何账号")
        return

    login_statuses = []
    renew_statuses = []

    with sync_playwright() as p:
        for i, account in enumerate(accounts):
            print(f"\n{'='*50}")
            print(f"处理账号 {i+1}/{len(accounts)}: {account['username']}")
            # 检查是否有续期API
            need_renew = 'renewApi' in account and account['renewApi']
            if need_renew:
                print(f"续期API: {account['renewApi']}")
            else:
                print(f"仅登录，不需要续期")
            print(f"{'='*50}\n")

            # 为每个账号创建一个新的浏览器实例
            browser = None
            context = None

            try:
                # 获取网站类型信息
                # 提取域名部分
                domain = account['site'].split('//')[1]
                # 分割域名并获取倒数第二段
                domain_parts = domain.split('.')
                if len(domain_parts) >= 2:
                    site_name = domain_parts[-2]  # 获取倒数第二段
                else:
                    site_name = domain
                need_renew = 'renewApi' in account and account['renewApi']
                # 如果没有renewApi字段，默认不需要获取Cookie
                need_cookie = account.get('needCookie', need_renew)

                print(f"为账号 {account['username']} 启动新的浏览器实例...")
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

                # 登录
                context, cookie, cf_clearance_cookie = login_and_get_cookie(account, browser)
                login_statuses.append(f"账号 {account['username']} ({site_name}) 登录成功")

                # 检查是否需要续期
                if need_renew:
                    # 确保有Cookie
                    if not cookie:
                        raise Exception("需要续期但未获取到Cookie")

                    print(f"账号 {account['username']} 配置了续期API，执行续期操作...")
                    result = renew_vps(account, context, cookie, cf_clearance_cookie)

                    # 尝试解析JSON并将Unicode转换为中文
                    try:
                        result_json = json.loads(result)
                        if 'msg' in result_json:
                            # 确保Unicode已经被正确解码为中文
                            result_json['msg'] = result_json['msg']
                            result_readable = json.dumps(result_json, ensure_ascii=False)
                        else:
                            result_readable = result
                    except:
                        result_readable = result

                    renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期成功: {result_readable}")
                    print(f"账号 {account['username']} 续期完成")
                else:
                    print(f"账号 {account['username']} 未配置续期API，仅执行登录操作")
                    renew_statuses.append(f"账号 {account['username']} ({site_name}) 仅执行登录，未进行续期")
            except Exception as e:
                print(f"账号 {account['username']} 处理出错: {str(e)}")

                # 获取网站类型信息用于状态消息
                try:
                    # 提取域名部分
                    domain = account['site'].split('//')[1]
                    # 分割域名并获取倒数第二段
                    domain_parts = domain.split('.')
                    if len(domain_parts) >= 2:
                        site_name = domain_parts[-2]  # 获取倒数第二段
                    else:
                        site_name = domain
                except:
                    site_name = account['site']

                if 'context' not in locals() or context is None:
                    login_statuses.append(f"账号 {account['username']} ({site_name}) 登录失败: {str(e)}")
                else:
                    login_statuses.append(f"账号 {account['username']} ({site_name}) 登录成功")

                # 检查是否是续期阶段出错
                need_renew = 'renewApi' in account and account['renewApi']
                if need_renew:
                    renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期失败: {str(e)}")
                else:
                    renew_statuses.append(f"账号 {account['username']} ({site_name}) 仅执行登录，未进行续期")
            finally:
                # 确保关闭浏览器上下文和浏览器实例
                if context:
                    print(f"关闭账号 {account['username']} 的浏览器上下文...")
                    context.close()
                if browser:
                    print(f"关闭账号 {account['username']} 的浏览器实例...")
                    browser.close()

                # 添加延迟，确保资源完全释放
                print("等待5秒，确保资源完全释放...")
                time.sleep(5)

    message = "Freecloud 登录与续期状态:\n\n" + "\n".join(login_statuses) + "\n\n" + "\n".join(renew_statuses)
    send_telegram_message(message)
    print("执行完成")

if __name__ == "__main__":
    try:
        print("开始执行脚本...")
        main()
        print("脚本执行完成")
    except Exception as e:
        import traceback
        print(f"脚本执行出错: {str(e)}")
        traceback.print_exc()
