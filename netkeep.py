import json
import os
import sys
import time
import random
import requests
import logging
import traceback
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("NetKeep")

# 调试函数
def debug_info(message, data=None, screenshot=None, account=None):
    """记录调试信息，可选择保存截图和数据"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 记录消息
    if account:
        logger.info(f"[{account['username']}] {message}")
    else:
        logger.info(message)

    # 如果提供了数据，保存到文件
    if data:
        try:
            filename = f"debug_logs/debug_{timestamp}"
            if account:
                filename += f"_{account['username']}"
            filename += ".json"

            with open(filename, 'w', encoding='utf-8') as f:
                if isinstance(data, str):
                    f.write(data)
                else:
                    json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"调试数据已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存调试数据失败: {str(e)}")

    # 如果提供了页面对象，保存截图
    if screenshot:
        try:
            filename = f"debug_screenshots/debug_{timestamp}"
            if account:
                filename += f"_{account['username']}"
            filename += ".png"

            screenshot.screenshot(path=filename)
            logger.info(f"调试截图已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存调试截图失败: {str(e)}")

# 处理配置文件
def process_config_file():
    """从分段的配置文件生成单行JSON格式的配置文件"""
    config_path = 'config.json'
    env_path = '.env'
    env_example_path = '.env.example'
    logger.info("环境变量NETKEEP_ACCOUNTS: %s", os.environ.get('NETKEEP_ACCOUNTS', '未设置'))

    # 检查是否存在config.json文件
    if os.path.exists(config_path):
        try:
            # 读取config.json文件内容
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()

            # 提取Telegram配置
            import re
            telegram_bot_token = None
            telegram_chat_id = None

            # 匹配Telegram配置
            bot_token_match = re.search(r'TELEGRAM_BOT_TOKEN=(.*?)$', config_content, re.MULTILINE)
            chat_id_match = re.search(r'TELEGRAM_CHAT_ID=(.*?)$', config_content, re.MULTILINE)

            if bot_token_match:
                telegram_bot_token = bot_token_match.group(1).strip()
            if chat_id_match:
                telegram_chat_id = chat_id_match.group(1).strip()

            # 提取FREECLOUD_ACCOUNTS或NETKEEP_ACCOUNTS数组
            accounts_match = re.search(r'(?:FREECLOUD_ACCOUNTS|NETKEEP_ACCOUNTS)=(\[.*?\])$', config_content, re.DOTALL | re.MULTILINE)
            accounts_data = []

            if accounts_match:
                try:
                    accounts_json = accounts_match.group(1)
                    accounts_data = json.loads(accounts_json)
                except json.JSONDecodeError as e:
                    print(f"无法解析账号数据，错误: {str(e)}")
                    # 尝试提取所有JSON对象
                    try:
                        pattern = r'({[^{}]*"site"[^{}]*"loginApi"[^{}]*})'
                        matches = re.findall(pattern, accounts_json, re.DOTALL)

                        if matches:
                            # 将提取的对象组合成一个数组
                            fixed_json = '[' + ','.join(matches) + ']'
                            accounts_data = json.loads(fixed_json)
                            print(f"成功从config.json中提取了 {len(accounts_data)} 个账号")
                        else:
                            print("无法从config.json中提取账号信息")
                    except Exception as e:
                        print(f"提取JSON对象失败: {str(e)}")
            else:
                # 如果没有找到NETKEEP_ACCOUNTS或FREECLOUD_ACCOUNTS变量，尝试直接提取JSON对象
                try:
                    pattern = r'({[^{}]*"site"[^{}]*"loginApi"[^{}]*})'
                    matches = re.findall(pattern, config_content, re.DOTALL)

                    if matches:
                        # 将提取的对象组合成一个数组
                        fixed_json = '[' + ','.join(matches) + ']'
                        accounts_data = json.loads(fixed_json)
                        print(f"成功从config.json中直接提取了 {len(accounts_data)} 个账号")
                    else:
                        print("无法从config.json中提取账号信息")
                except Exception as e:
                    print(f"直接提取JSON对象失败: {str(e)}")

            # 确保.env文件存在，如果不存在则从.env.example创建
            if not os.path.exists(env_path) and os.path.exists(env_example_path):
                with open(env_example_path, 'r', encoding='utf-8') as f:
                    env_example_content = f.read()
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(env_example_content)
                print("已从.env.example创建.env文件")
            elif not os.path.exists(env_path) and not os.path.exists(env_example_path):
                # 如果.env和.env.example都不存在，创建一个基本的.env文件
                basic_env_content = """# NetKeep配置文件
# 自动生成的.env文件

# 账号信息（JSON格式）
NETKEEP_ACCOUNTS=[]

# Telegram通知配置
# TELEGRAM_BOT_TOKEN=your_bot_token
# TELEGRAM_CHAT_ID=your_chat_id
"""
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(basic_env_content)
                print("已创建基本的.env文件")

            # 读取.env文件内容
            if os.path.exists(env_path):
                with open(env_path, 'r', encoding='utf-8') as f:
                    env_content = f.read()

                # 更新NETKEEP_ACCOUNTS
                pattern_accounts = r'NETKEEP_ACCOUNTS=\[.*?\]'
                compact_json = json.dumps(accounts_data, ensure_ascii=False, separators=(',', ':'))

                if re.search(pattern_accounts, env_content, re.DOTALL):
                    new_env_content = re.sub(pattern_accounts, f'NETKEEP_ACCOUNTS={compact_json}', env_content, flags=re.DOTALL)
                else:
                    # 如果没有找到NETKEEP_ACCOUNTS行，添加一个
                    new_env_content = env_content + f"\nNETKEEP_ACCOUNTS={compact_json}\n"

                # 更新Telegram配置
                if telegram_bot_token:
                    pattern_bot_token = r'#?\s*TELEGRAM_BOT_TOKEN=.*?$'
                    if re.search(pattern_bot_token, new_env_content, re.MULTILINE):
                        new_env_content = re.sub(pattern_bot_token, f'TELEGRAM_BOT_TOKEN={telegram_bot_token}', new_env_content, flags=re.MULTILINE)
                    else:
                        new_env_content += f"\nTELEGRAM_BOT_TOKEN={telegram_bot_token}\n"

                if telegram_chat_id:
                    pattern_chat_id = r'#?\s*TELEGRAM_CHAT_ID=.*?$'
                    if re.search(pattern_chat_id, new_env_content, re.MULTILINE):
                        new_env_content = re.sub(pattern_chat_id, f'TELEGRAM_CHAT_ID={telegram_chat_id}', new_env_content, flags=re.MULTILINE)
                    else:
                        new_env_content += f"\nTELEGRAM_CHAT_ID={telegram_chat_id}\n"

                # 写入新的.env文件
                with open(env_path, 'w', encoding='utf-8') as f:
                    f.write(new_env_content)

                print("已从config.json生成配置")

                # 将账号信息设置到环境变量中，以便main函数可以直接使用
                os.environ['NETKEEP_ACCOUNTS'] = compact_json
                if telegram_bot_token:
                    os.environ['TELEGRAM_BOT_TOKEN'] = telegram_bot_token
                if telegram_chat_id:
                    os.environ['TELEGRAM_CHAT_ID'] = telegram_chat_id
            else:
                print("未找到.env文件，无法更新配置")
        except Exception as e:
            print(f"处理配置文件时出错: {str(e)}")

# 处理配置文件并加载.env文件
process_config_file()
load_dotenv(override=True)  # 使用override=True强制重新加载.env文件


def send_telegram_message(message):
    """发送Telegram通知，如果配置缺失则只打印消息"""
    # 检查Telegram配置是否存在
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    # 如果Telegram配置缺失，只打印消息
    if not (bot_token and chat_id):
        print("Telegram配置缺失: 跳过Telegram通知")
        # 打印消息内容
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

def login_and_get_cookie(account, browser, max_retries=3):  # 增加重试次数
    # 检查是否需要获取Cookie
    # 如果没有renewApi字段，默认不需要获取Cookie
    need_cookie = account.get('needCookie', 'renewApi' in account)

    # 使用更真实的浏览器配置
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        viewport={'width': 1280, 'height': 800},
        extra_http_headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
    )

    # 启用JavaScript
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => false})")

    page = context.new_page()

    # 随机移动鼠标，模拟人类行为
    def simulate_human_behavior(page):
        # 随机移动鼠标
        import random
        for _ in range(3):
            page.mouse.move(
                random.randint(100, 1000),
                random.randint(100, 600)
            )
            time.sleep(random.uniform(0.5, 1.5))

    for attempt in range(max_retries):
        try:
            login_url = f"{account['site']}{account['loginApi']}"
            print(f"尝试 {attempt + 1}/{max_retries}: 导航到 {login_url} 登录 {account['username']}")

            # 使用networkidle等待所有网络请求完成
            page.goto(login_url, wait_until='networkidle', timeout=120000)

            # 检查是否遇到CloudFlare挑战页面
            if page.content().find("Just a moment") > -1 or page.content().find("Checking your browser") > -1:
                print("检测到CloudFlare挑战页面，等待挑战完成...")
                # 等待更长时间让CloudFlare挑战完成
                for i in range(12):  # 最多等待60秒
                    time.sleep(5)
                    if page.content().find("Just a moment") == -1 and page.content().find("Checking your browser") == -1:
                        print("CloudFlare挑战已完成，继续执行...")
                        break

                # 如果仍然在CloudFlare页面，尝试刷新
                if page.content().find("Just a moment") > -1 or page.content().find("Checking your browser") > -1:
                    print("CloudFlare挑战仍未完成，尝试刷新页面...")
                    page.reload(wait_until='networkidle', timeout=120000)
                    time.sleep(5)

            # 模拟人类行为
            simulate_human_behavior(page)

            # 填写表单
            print("填写登录表单...")

            # 尝试不同的用户名输入框选择器
            username_selectors = ['input[name="username"]', 'input[name="email"]', 'input[id="username"]', 'input[id="email"]']
            for selector in username_selectors:
                if page.locator(selector).count() > 0:
                    print(f"找到用户名输入框: {selector}")
                    page.fill(selector, account['username'])
                    break

            # 尝试不同的密码输入框选择器
            password_selectors = ['input[name="password"]', 'input[id="password"]', 'input[type="password"]']
            for selector in password_selectors:
                if page.locator(selector).count() > 0:
                    print(f"找到密码输入框: {selector}")
                    page.fill(selector, account['password'])
                    break

            # 尝试勾选"记住我"选项
            page.evaluate('() => { const remember = document.querySelector(\'input[name="remember"]\'); if (remember) remember.checked = true; }')

            # 模拟人类行为
            simulate_human_behavior(page)

            # 提交登录
            print(f"提交登录表单...")

            # 尝试不同的登录按钮选择器
            login_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("登录")',
                'button:has-text("Login")',
                'a:has-text("登录")',
                'a:has-text("Login")'
            ]

            login_button_found = False
            for selector in login_button_selectors:
                if page.locator(selector).count() > 0:
                    print(f"找到登录按钮: {selector}")
                    page.locator(selector).first.click()
                    login_button_found = True
                    break

            if not login_button_found:
                print("未找到登录按钮，尝试提交表单...")
                page.evaluate('() => { const form = document.querySelector("form"); if (form) form.submit(); }')

            # 等待页面加载完成
            page.wait_for_load_state('networkidle', timeout=120000)

            # 等待一段时间，确保登录完成
            print(f"等待5秒，确保登录完成...")
            time.sleep(5)

            # 检查是否登录成功
            # 可能的登录失败提示
            failure_texts = ["密码错误", "用户名错误", "登录失败", "incorrect password", "invalid username"]
            page_content = page.content().lower()

            for text in failure_texts:
                if text.lower() in page_content:
                    raise Exception(f"登录失败，页面提示: '{text}'")

            # 只有需要获取Cookie时才访问 /server/lxc 建立会话
            if need_cookie:
                print(f"导航到 {account['site']}/server/lxc 页面...")
                page.goto(f"{account['site']}/server/lxc", wait_until='networkidle', timeout=120000)

                # 检查是否遇到CloudFlare挑战页面
                if page.content().find("Just a moment") > -1 or page.content().find("Checking your browser") > -1:
                    print("服务器页面遇到CloudFlare挑战，等待挑战完成...")
                    # 等待更长时间让CloudFlare挑战完成
                    for i in range(12):  # 最多等待60秒
                        time.sleep(5)
                        if page.content().find("Just a moment") == -1 and page.content().find("Checking your browser") == -1:
                            print("CloudFlare挑战已完成，继续执行...")
                            break
            else:
                print(f"不需要获取Cookie，跳过导航到 {account['site']}/server/lxc 页面")

            # 如果需要获取Cookie
            if need_cookie:
                # 获取所有Cookie
                cookies = context.cookies()

                # 尝试获取sw110xy cookie
                sw110xy_cookie = next((c for c in cookies if c['name'] == 'sw110xy'), None)

                # 获取CloudFlare cookie
                cf_clearance_cookie = next((c for c in cookies if c['name'] == 'cf_clearance'), None)

                # 如果找不到sw110xy cookie，尝试获取其他可能的会话cookie
                if not sw110xy_cookie:
                    # 尝试获取其他常见的会话cookie
                    session_cookies = [
                        next((c for c in cookies if c['name'] == 'PHPSESSID'), None),
                        next((c for c in cookies if c['name'] == 'laravel_session'), None),
                        next((c for c in cookies if c['name'] == 'session'), None),
                        next((c for c in cookies if 'session' in c['name'].lower()), None)
                    ]

                    # 使用第一个非None的会话cookie
                    session_cookie = next((c for c in session_cookies if c is not None), None)

                    if session_cookie:
                        print(f"未找到sw110xy cookie，使用替代会话cookie: {session_cookie['name']}")
                        cookie_value = f"{session_cookie['name']}={session_cookie['value']};1"
                    else:
                        # 如果没有找到任何会话cookie，尝试使用所有cookie
                        print("未找到任何会话cookie，使用所有cookie")
                        cookie_value = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
                else:
                    cookie_value = f"{sw110xy_cookie['name']}={sw110xy_cookie['value']};1"

                print(f"账号 {account['username']} 登录成功，Cookie: {cookie_value}")

                # 截图保存登录成功状态
                page.screenshot(path=f"login_success_{account['username']}.png")

                return context, cookie_value, cf_clearance_cookie
            else:
                # 不需要获取Cookie，只需登录
                print(f"账号 {account['username']} 登录成功，不需要获取Cookie")
                return context, None, None
        except PlaywrightTimeoutError as e:
            print(f"账号 {account['username']} 登录尝试 {attempt + 1} 失败: {str(e)}")
            # 保存超时时的截图
            try:
                page.screenshot(path=f"login_timeout_{account['username']}_{attempt}.png")
            except:
                pass

            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
        except Exception as e:
            print(f"账号 {account['username']} 登录失败: {str(e)}")
            # 保存失败时的截图
            try:
                page.screenshot(path=f"login_error_{account['username']}_{attempt}.png")
            except:
                pass

            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
        finally:
            page.close()

def renew_vps(account, context, cookie, cf_clearance_cookie=None, max_retries=3):
    page = context.new_page()

    try:
        for attempt in range(max_retries):
            try:
                # 导航到服务器列表页面
                print(f"尝试 {attempt + 1}/{max_retries}: 导航到 {account['site']}/server/lxc 页面...")
                page.goto(f"{account['site']}/server/lxc", wait_until='networkidle', timeout=120000)  # 使用networkidle等待所有网络请求完成

                # 等待页面完全加载，处理可能的CloudFlare挑战
                print(f"等待5秒，确保页面完全加载并处理CloudFlare挑战...")
                time.sleep(5)

                # 检查是否遇到CloudFlare挑战页面
                if page.content().find("Just a moment") > -1 or page.content().find("Checking your browser") > -1:
                    print("检测到CloudFlare挑战页面，等待挑战完成...")
                    # 等待更长时间让CloudFlare挑战完成
                    for i in range(12):  # 最多等待60秒
                        time.sleep(5)
                        if page.content().find("Just a moment") == -1 and page.content().find("Checking your browser") == -1:
                            print("CloudFlare挑战已完成，继续执行...")
                            break

                    # 如果仍然在CloudFlare页面，尝试刷新
                    if page.content().find("Just a moment") > -1 or page.content().find("Checking your browser") > -1:
                        print("CloudFlare挑战仍未完成，尝试刷新页面...")
                        page.reload(wait_until='networkidle', timeout=120000)
                        time.sleep(5)

                # 获取续期URL
                renew_url = f"{account['site']}{account['renewApi']}"
                print(f"账号 {account['username']} 的续期URL: {renew_url}")

                # 方法1: 直接访问续期页面并点击续期按钮
                try:
                    debug_info(f"方法1: 直接访问续期页面 {renew_url}", account=account)

                    # 保存续期前的页面内容和截图
                    debug_info("续期前页面状态", data=page.content(), screenshot=page, account=account)

                    page.goto(renew_url, wait_until='networkidle', timeout=120000)

                    # 等待页面加载
                    time.sleep(5)

                    # 保存导航后的页面内容和截图
                    debug_info("续期页面导航后状态", data=page.content(), screenshot=page, account=account)

                    # 检查是否遇到CloudFlare挑战页面
                    if page.content().find("Just a moment") > -1 or page.content().find("Checking your browser") > -1:
                        debug_info("续期页面遇到CloudFlare挑战，等待挑战完成...", screenshot=page, account=account)
                        # 等待更长时间让CloudFlare挑战完成
                        for i in range(12):  # 最多等待60秒
                            time.sleep(5)
                            if page.content().find("Just a moment") == -1 and page.content().find("Checking your browser") == -1:
                                debug_info("CloudFlare挑战已完成，继续执行...", screenshot=page, account=account)
                                break

                    # 查找并点击续期按钮
                    renew_button_found = False

                    # 尝试多种可能的续期按钮选择器
                    selectors = [
                        'button:has-text("续期")',
                        'a:has-text("续期")',
                        'button.btn-renew',
                        'a.btn-renew',
                        'button[type="submit"]:has-text("续期")',
                        'input[type="submit"][value="续期"]',
                        'button.btn-primary:has-text("续期")',
                        'a.btn-primary:has-text("续期")'
                    ]

                    # 记录所有可见元素，帮助调试
                    all_buttons = []
                    for selector in ['button', 'a.btn', 'input[type="submit"]', 'a[href*="renew"]']:
                        elements = page.locator(selector).all()
                        for element in elements:
                            try:
                                text = element.text_content()
                                all_buttons.append({"selector": selector, "text": text})
                            except:
                                pass

                    debug_info("页面上的所有按钮元素", data=all_buttons, account=account)

                    for selector in selectors:
                        if page.locator(selector).count() > 0:
                            debug_info(f"找到续期按钮: {selector}", account=account)
                            # 点击前截图
                            debug_info("点击续期按钮前", screenshot=page, account=account)

                            try:
                                # 尝试使用JavaScript点击
                                page.evaluate(f'document.querySelector("{selector}").click()')
                                debug_info("使用JavaScript点击续期按钮", account=account)
                            except:
                                # 如果JavaScript点击失败，使用Playwright点击
                                page.locator(selector).first.click()
                                debug_info("使用Playwright点击续期按钮", account=account)

                            renew_button_found = True
                            # 等待页面响应
                            time.sleep(3)
                            # 点击后截图
                            debug_info("点击续期按钮后", screenshot=page, account=account)
                            break

                    if not renew_button_found:
                        debug_info("未找到续期按钮，尝试方法2...", screenshot=page, account=account)
                        raise Exception("未找到续期按钮")

                    # 检查是否有确认对话框
                    confirm_selectors = [
                        'button:has-text("确定")',
                        'button:has-text("确认")',
                        'button.btn-primary:has-text("确定")',
                        'button.btn-confirm',
                        'button[type="submit"]:has-text("确定")'
                    ]

                    # 记录所有可见的确认按钮
                    all_confirm_buttons = []
                    for selector in ['button', 'input[type="submit"]']:
                        elements = page.locator(selector).all()
                        for element in elements:
                            try:
                                text = element.text_content()
                                all_confirm_buttons.append({"selector": selector, "text": text})
                            except:
                                pass

                    debug_info("页面上的所有确认按钮元素", data=all_confirm_buttons, account=account)

                    confirm_button_found = False
                    for selector in confirm_selectors:
                        if page.locator(selector).count() > 0:
                            debug_info(f"找到确认按钮: {selector}", screenshot=page, account=account)

                            try:
                                # 尝试使用JavaScript点击
                                page.evaluate(f'document.querySelector("{selector}").click()')
                                debug_info("使用JavaScript点击确认按钮", account=account)
                            except:
                                # 如果JavaScript点击失败，使用Playwright点击
                                page.locator(selector).first.click()
                                debug_info("使用Playwright点击确认按钮", account=account)

                            confirm_button_found = True
                            time.sleep(3)
                            debug_info("点击确认按钮后", screenshot=page, account=account)
                            break

                    if confirm_button_found:
                        debug_info("已点击确认按钮", account=account)
                    else:
                        debug_info("未找到确认按钮", account=account)

                    # 检查续期结果
                    success_texts = ["续期成功", "已续期", "操作成功", "success"]
                    page_content = page.content().lower()

                    # 保存最终页面内容
                    debug_info("续期操作后页面内容", data=page_content, account=account)

                    success = False
                    for text in success_texts:
                        if text.lower() in page_content:
                            success = True
                            debug_info(f"检测到成功信息: '{text}'", account=account)
                            break

                    if success:
                        debug_info("续期成功", screenshot=page, account=account)
                        return "续期成功"
                    else:
                        # 如果页面上没有成功信息，尝试方法2
                        debug_info("未检测到续期成功信息，尝试方法2...", screenshot=page, account=account)
                        raise Exception("未检测到续期成功信息")

                except Exception as e:
                    debug_info(f"方法1失败: {str(e)}，尝试方法2...", account=account)
                    # 保存异常堆栈信息
                    debug_info("方法1失败详细信息", data=traceback.format_exc(), account=account)

                # 方法2: 使用API请求续期
                try:
                    debug_info(f"方法2: 使用API请求续期", account=account)
                    # 先导航到服务器列表页面建立会话
                    debug_info("导航到服务器列表页面建立会话", account=account)
                    page.goto(f"{account['site']}/server/lxc", wait_until='networkidle', timeout=120000)
                    time.sleep(3)

                    # 保存服务器列表页面状态
                    debug_info("服务器列表页面状态", data=page.content(), screenshot=page, account=account)

                    # 获取所有cookie
                    cookies = context.cookies()
                    debug_info("当前会话Cookie", data=cookies, account=account)

                    # 设置请求头
                    headers = {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-Requested-With': 'XMLHttpRequest',
                        'Referer': f"{account['site']}/server/lxc",
                        'Origin': account['site'],
                        'User-Agent': page.evaluate('() => navigator.userAgent'),
                        'Cookie': cookie  # 使用登录时获取的cookie
                    }

                    # 如果有CloudFlare cookie，添加到请求头
                    if cf_clearance_cookie:
                        headers['Cookie'] += f"; cf_clearance={cf_clearance_cookie['value']}"

                    debug_info("API请求头", data=headers, account=account)

                    # 设置请求体
                    data = {
                        'month': '1',
                        'coupon_id': '0',
                        'submit': '1'
                    }

                    debug_info("API请求体", data=data, account=account)

                    # 发送POST请求
                    debug_info(f"正在为账号 {account['username']} 提交续期API请求...", account=account)

                    # 尝试使用fetch API
                    try:
                        debug_info("尝试使用浏览器的fetch API发送请求", account=account)
                        fetch_result = page.evaluate(f'''
                            async () => {{
                                try {{
                                    const response = await fetch("{renew_url}", {{
                                        method: 'POST',
                                        headers: {{
                                            'Content-Type': 'application/x-www-form-urlencoded',
                                            'X-Requested-With': 'XMLHttpRequest'
                                        }},
                                        body: 'month=1&coupon_id=0&submit=1',
                                        credentials: 'include'
                                    }});

                                    const status = response.status;
                                    const text = await response.text();
                                    return {{ status, text }};
                                }} catch (error) {{
                                    return {{ error: error.toString() }};
                                }}
                            }}
                        ''')

                        debug_info("fetch API结果", data=fetch_result, account=account)

                        if 'error' in fetch_result:
                            debug_info(f"fetch API失败: {fetch_result['error']}", account=account)
                            raise Exception(f"fetch API失败: {fetch_result['error']}")

                        status = fetch_result['status']
                        response_text = fetch_result['text']
                    except Exception as e:
                        debug_info(f"fetch API异常: {str(e)}，尝试使用Playwright请求", account=account)

                        # 如果fetch API失败，使用Playwright的请求API
                        response = page.request.post(
                            renew_url,
                            headers=headers,
                            form=data
                        )

                        # 获取响应
                        status = response.status
                        response_text = response.text()

                    debug_info(f"账号 {account['username']} 续期响应状态码: {status}", account=account)
                    debug_info(f"账号 {account['username']} 续期响应内容", data=response_text, account=account)

                    # 如果请求成功，返回响应文本
                    if status == 200:
                        # 检查响应内容是否包含成功信息
                        success_texts = ["续期成功", "已续期", "操作成功", "success"]
                        success = False

                        for text in success_texts:
                            if text.lower() in response_text.lower():
                                success = True
                                debug_info(f"API响应中检测到成功信息: '{text}'", account=account)
                                break

                        if success:
                            debug_info("API续期成功", account=account)
                            return response_text
                        else:
                            debug_info("API响应状态码为200，但未检测到成功信息", data=response_text, account=account)
                            # 尝试导航到续期页面查看结果
                            try:
                                page.goto(renew_url, wait_until='networkidle', timeout=120000)
                                debug_info("续期后页面状态", screenshot=page, account=account)
                            except:
                                pass

                            return response_text
                    else:
                        debug_info(f"续期请求返回非200状态码: {status}", data=response_text, account=account)

                        # 检查是否是CloudFlare挑战
                        if "Just a moment" in response_text or "Checking your browser" in response_text:
                            debug_info("API请求被CloudFlare拦截", account=account)

                        if attempt < max_retries - 1:
                            debug_info(f"等待5秒后重试...", account=account)
                            time.sleep(5)
                            continue
                        else:
                            raise Exception(f"续期请求失败，状态码: {status}")
                except Exception as e:
                    debug_info(f"方法2失败: {str(e)}", account=account)
                    # 保存异常堆栈信息
                    debug_info("方法2失败详细信息", data=traceback.format_exc(), account=account)

                    if attempt < max_retries - 1:
                        debug_info(f"等待5秒后重试...", account=account)
                        time.sleep(5)
                        continue
                    raise
            except Exception as e:
                debug_info(f"续期尝试 {attempt + 1} 失败: {str(e)}", account=account)
                # 保存异常堆栈信息
                debug_info("续期失败详细信息", data=traceback.format_exc(), account=account)
                # 保存当前页面状态
                try:
                    debug_info("续期失败时页面状态", screenshot=page, account=account)
                except:
                    pass

                if attempt < max_retries - 1:
                    debug_info(f"等待5秒后重试...", account=account)
                    time.sleep(5)
                    continue
                raise
        # 如果所有尝试都失败，抛出异常
        raise Exception(f"所有 {max_retries} 次续期尝试都失败")
    finally:
        page.close()

def main():
    # 创建调试目录
    os.makedirs("debug_screenshots", exist_ok=True)
    os.makedirs("debug_logs", exist_ok=True)

    # 记录系统信息
    debug_info("NetKeep启动", data={
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Python版本": sys.version,
        "操作系统": os.name,
        "环境变量": {k: v for k, v in os.environ.items() if not ("password" in k.lower() or "token" in k.lower() or "secret" in k.lower())}
    })

    # 从环境变量加载账号信息
    # 兼容旧的FREECLOUD_ACCOUNTS变量名
    netkeep_accounts_env = os.environ.get('NETKEEP_ACCOUNTS', os.environ.get('FREECLOUD_ACCOUNTS', '[]'))

    # 记录原始环境变量值，用于调试
    logger.info("原始NETKEEP_ACCOUNTS环境变量值: %s", netkeep_accounts_env)

    try:
        # 尝试直接解析JSON
        accounts = json.loads(netkeep_accounts_env)
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {str(e)}")
        print("尝试修复JSON格式...")

        # 检查是否是不完整的JSON数组
        if not netkeep_accounts_env.strip().startswith('['):
            # 如果不是以[开头，尝试添加[]
            try:
                # 尝试将内容包装在[]中
                fixed_json = '[' + netkeep_accounts_env.strip() + ']'
                accounts = json.loads(fixed_json)
                print("成功修复JSON格式")
            except json.JSONDecodeError:
                # 如果仍然失败，尝试使用正则表达式提取JSON对象
                import re
                try:
                    # 尝试提取所有JSON对象
                    pattern = r'({[^{}]*"site"[^{}]*"loginApi"[^{}]*})'
                    matches = re.findall(pattern, netkeep_accounts_env, re.DOTALL)

                    if matches:
                        # 将提取的对象组合成一个数组
                        accounts_json = '[' + ','.join(matches) + ']'
                        accounts = json.loads(accounts_json)
                        print(f"成功从环境变量中提取了 {len(accounts)} 个账号")
                    else:
                        print("无法从环境变量中提取账号信息")
                        accounts = []
                except Exception as e:
                    print(f"提取JSON对象失败: {str(e)}")
                    accounts = []
        else:
            # 如果已经是以[开头，可能是其他JSON格式问题
            print("环境变量格式不正确，无法解析")
            accounts = []

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



    if not accounts:
        print("NETKEEP_ACCOUNTS 或 FREECLOUD_ACCOUNTS 环境变量中未配置任何账号")
        send_telegram_message("NetKeep 续期失败: 没有配置任何账号")
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
                # 使用更多的浏览器参数，以更好地处理CloudFlare挑战
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-web-security',
                        '--disable-features=IsolateOrigins,site-per-process',
                        '--ignore-certificate-errors',
                        '--disable-extensions',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                )

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

    message = "NetKeep 登录与续期状态:\n\n" + "\n".join(login_statuses) + "\n\n" + "\n".join(renew_statuses)
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
