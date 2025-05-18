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
<<<<<<< HEAD
    level=logging.WARNING,  # 将日志级别从INFO改为WARNING，这样INFO级别的消息将不会显示
=======
    level=logging.INFO,
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("NetKeep")

<<<<<<< HEAD
# 调试函数 - 简化版，由于日志级别设置为WARNING，INFO级别的日志不会显示
def debug_info(message, data=None, account=None, step_name=None):
    """空函数，由于日志级别设置为WARNING，所有INFO级别的日志都不会显示"""
    pass
=======
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
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

# 处理配置文件
def process_config_file():
    """从分段的配置文件生成单行JSON格式的配置文件"""
    config_path = 'config.json'
    env_path = '.env'
    env_example_path = '.env.example'
<<<<<<< HEAD
=======
    logger.info("环境变量NETKEEP_ACCOUNTS: %s", os.environ.get('NETKEEP_ACCOUNTS', '未设置'))
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

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

            # 提取NETKEEP_ACCOUNTS数组
            accounts_match = re.search(r'NETKEEP_ACCOUNTS=(\[.*?\])$', config_content, re.DOTALL | re.MULTILINE)
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
                # 如果没有找到NETKEEP_ACCOUNTS变量，尝试直接提取JSON对象
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

def login_and_get_cookie(account, browser, max_retries=2):  # 减少重试次数
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

            # 使用load而不是networkidle，更快地返回控制权
            try:
                page.goto(login_url, wait_until='load', timeout=30000)
            except Exception as e:
                print(f"页面导航时出错: {str(e)}，尝试继续执行...")

            # 检查是否遇到CloudFlare挑战页面
            try:
                page_content = page.content().lower()
                if "just a moment" in page_content or "checking your browser" in page_content:
                    print("检测到CloudFlare挑战页面，等待挑战完成...")
                    # 等待更长时间让CloudFlare挑战完成
                    for _ in range(6):  # 最多等待30秒
                        time.sleep(5)
                        page_content = page.content().lower()
                        if "just a moment" not in page_content and "checking your browser" not in page_content:
                            print("CloudFlare挑战已完成，继续执行...")
                            break

                    # 如果仍然在CloudFlare页面，尝试刷新
                    if "just a moment" in page_content or "checking your browser" in page_content:
                        print("CloudFlare挑战仍未完成，尝试刷新页面...")
                        try:
                            page.reload(wait_until='load', timeout=30000)
                        except Exception as e:
                            print(f"页面刷新时出错: {str(e)}，尝试继续执行...")
                        time.sleep(5)
            except Exception as e:
                print(f"检查CloudFlare挑战时出错: {str(e)}，尝试继续执行...")

            # 填写表单
            print("填写登录表单...")

            # 使用netkeep1.py的简单直接的表单填写方式
            try:
                # 直接填写用户名和密码
                page.fill('input[name="username"]', account['username'])
                page.fill('input[name="password"]', account['password'])

                # 尝试勾选"记住我"选项
                page.evaluate('() => { const remember = document.querySelector(\'input[name="remember"]\'); if (remember) remember.checked = true; }')
            except Exception as e:
                print(f"使用简单方式填写表单失败: {str(e)}")
                print("尝试使用备用方式填写表单...")

                # 备用方式：尝试不同的选择器
                try:
                    # 尝试不同的用户名输入框选择器
                    username_selectors = ['input[name="email"]', 'input[id="username"]', 'input[id="email"]']
                    for selector in username_selectors:
                        try:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, account['username'])
                                break
                        except Exception:
                            continue

                    # 尝试不同的密码输入框选择器
                    password_selectors = ['input[id="password"]', 'input[type="password"]']
                    for selector in password_selectors:
                        try:
                            if page.locator(selector).count() > 0:
                                page.fill(selector, account['password'])
                                break
                        except Exception:
                            continue
                except Exception as e:
                    print(f"备用方式填写表单也失败: {str(e)}")

            # 提交登录表单并立即开始轮询
            print(f"提交登录表单并立即开始轮询...")

            # 使用netkeep1.py的简单直接的登录方式
            try:
                # 直接点击提交按钮
                print(f"点击登录按钮...")
                page.click('button[type="submit"]')
            except Exception as e:
                print(f"直接点击登录按钮失败: {str(e)}")
                print("尝试使用备用方式提交表单...")

                # 备用方式：尝试不同的方法提交表单
                try:
                    # 尝试使用JavaScript提交表单
                    page.evaluate('() => { const form = document.querySelector("form"); if (form) form.submit(); }')
                    print("已通过JavaScript提交表单")
                except Exception as js_error:
                    print(f"通过JavaScript提交表单失败: {str(js_error)}")

                    # 尝试点击其他可能的登录按钮
                    login_button_selectors = [
                        'input[type="submit"]',
                        'button:has-text("登录")', 'button:has-text("Login")',
                        'a:has-text("登录")', 'a:has-text("Login")'
                    ]

                    for selector in login_button_selectors:
                        try:
                            if page.locator(selector).count() > 0:
                                page.click(selector)
                                print(f"已点击登录按钮: {selector}")
                                break
                        except Exception:
                            continue

            # 立即开始轮询，不等待页面加载
            print(f"开始轮询检测登录状态...")
            start_time = time.time()
            max_wait_time = 30  # 最多等待30秒，比netkeep1.py的等待时间长，但比原来的60秒短
            login_success_detected = False
            poll_count = 0

            # 使用更短的初始检查间隔
            while time.time() - start_time < max_wait_time:
                poll_count += 1
                current_poll_time = time.time() - start_time

                # 前10秒使用更短的检查间隔
                current_interval = 0.5 if current_poll_time < 10 else 2

                try:
                    # 检查当前URL（最快的检查方式）
                    current_url = page.url
                    url_changed = login_url != current_url and "/login" not in current_url

                    # 减少日志输出，只在特定间隔输出
                    if poll_count % 5 == 0 or poll_count < 5:
                        print(f"轮询 #{poll_count} (耗时: {current_poll_time:.2f}秒) - 当前URL: {current_url}")
                        print(f"URL是否改变: {url_changed}")

                    if url_changed:
                        # URL已改变，检查是否有登录表单
                        login_form_exists = False
                        try:
                            login_form_exists = page.locator('form input[type="password"]').count() > 0
                        except Exception:
                            pass

                        if not login_form_exists:
                            # URL已改变且没有登录表单，很可能已经登录成功
                            print(f"URL已改变且无登录表单，检测到登录成功 (耗时: {current_poll_time:.2f}秒)")
                            login_success_detected = True
                            break
                    else:
                        # 如果URL未改变，每隔几次轮询进行一次完整检查
                        if poll_count % 5 == 0:
                            try:
                                page_content = page.content().lower()
                                login_form_exists = page.locator('form input[type="password"]').count() > 0

                                # 检查页面内容是否包含客户区域特征
                                client_area_indicators = [
                                    "client area", "客户中心", "用户中心", "控制面板",
                                    "hosting plans", "support tickets", "dashboard", "account"
                                ]

                                if any(indicator in page_content for indicator in client_area_indicators) and not login_form_exists:
                                    print(f"页面内容表明登录成功且无登录表单，检测到登录成功 (耗时: {current_poll_time:.2f}秒)")
                                    login_success_detected = True
                                    break
                            except Exception as e:
                                if poll_count % 10 == 0:
                                    print(f"完整检查时出错: {str(e)}")
                except Exception as e:
                    if poll_count % 10 == 0:
                        print(f"轮询检查时出错: {str(e)}")

                # 减少轮询状态输出
                if poll_count % 10 == 0:
                    print(f"继续轮询... (已轮询: {poll_count}次, 耗时: {current_poll_time:.2f}秒)")

                time.sleep(current_interval)

            # 轮询结束后的最终检查
            print(f"轮询结束，进行最终检查")

            try:
                # 获取最终的页面状态
                current_url = page.url
                url_changed = login_url != current_url and "/login" not in current_url

                print(f"最终检查 - 当前URL: {current_url}")

                # 快速检查登录状态
                login_form_exists = False
                content_indicates_success = False
                failure_detected = False

                try:
                    # 检查是否仍有登录表单
                    login_form_exists = page.locator('form input[type="password"]').count() > 0

                    # 检查页面内容
                    page_content = page.content().lower()

                    # 检查成功指标
                    client_area_indicators = ["client area", "客户中心", "用户中心", "控制面板",
                                             "hosting plans", "support tickets", "dashboard", "account"]
                    content_indicates_success = any(indicator in page_content for indicator in client_area_indicators)

                    # 检查失败指标
                    failure_texts = ["密码错误", "用户名错误", "登录失败", "incorrect password", "invalid username"]
                    failure_detected = any(text in page_content for text in failure_texts)
                except Exception as e:
                    print(f"检查页面状态时出错: {str(e)}")

                # 如果轮询中未检测到成功，再次检查
                if not login_success_detected:
                    if (url_changed or content_indicates_success) and not login_form_exists:
                        login_success_detected = True

                # 最终判断
                if login_success_detected:
                    print(f"最终判断: 登录成功")
                elif failure_detected:
                    print(f"最终判断: 登录失败 (检测到失败提示)")
                    raise Exception(f"登录失败，检测到失败提示")
                elif login_form_exists:
                    print(f"最终判断: 登录失败 (仍存在登录表单)")
                    raise Exception("登录失败，仍存在登录表单")
                elif url_changed:
                    print(f"最终判断: 登录成功 (URL已改变)")
                    login_success_detected = True
                elif content_indicates_success:
                    print(f"最终判断: 登录成功 (页面内容包含客户区域特征)")
                    login_success_detected = True
                else:
                    print(f"最终判断: 无法确定登录状态")
                    raise Exception("登录超时，未能确认登录状态")
            except Exception as e:
                if not login_success_detected:
                    raise

            # 只有需要获取Cookie时才访问 /server/lxc 建立会话
            if need_cookie:
                print(f"导航到 {account['site']}/server/lxc 页面...")
                page.goto(f"{account['site']}/server/lxc", wait_until='networkidle', timeout=12000)

                # 检查是否遇到CloudFlare挑战页面
                if "Just a moment" in page.content() or "Checking your browser" in page.content():
                    print("服务器页面遇到CloudFlare挑战，等待挑战完成...")
                    # 等待更长时间让CloudFlare挑战完成
                    for _ in range(12):  # 最多等待30秒
                        time.sleep(5)
                        if "Just a moment" not in page.content() and "Checking your browser" not in page.content():
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

                # 登录成功

                return context, cookie_value, cf_clearance_cookie
            else:
                # 不需要获取Cookie，只需登录
                print(f"账号 {account['username']} 登录成功，不需要获取Cookie")
                return context, None, None
        except PlaywrightTimeoutError as e:
            # 这个异常处理部分现在应该很少触发，因为我们使用了自定义轮询
            print(f"Playwright超时异常: {str(e)}")

            # 检查页面状态
            try:
                # 检查当前URL和页面内容
                current_url = page.url
                url_changed = login_url != current_url and "/login" not in current_url

                # 快速检查登录状态
                try:
                    login_form_exists = page.locator('form input[type="password"]').count() > 0
                    page_content = page.content().lower()
                    client_area_indicators = ["client area", "客户中心", "用户中心", "控制面板", "dashboard", "account"]
                    content_indicates_success = any(indicator in page_content for indicator in client_area_indicators)

                    # 如果URL已改变或页面内容表明登录成功，且没有登录表单，则认为登录成功
                    if (url_changed or content_indicates_success) and not login_form_exists:
                        print(f"虽然发生超时，但检测到登录成功")
                        return context, None, None
                except Exception:
                    pass
            except Exception:
                pass

            print(f"账号 {account['username']} 登录尝试 {attempt + 1} 失败")

            if attempt < max_retries - 1:
                print(f"等待10秒后重试...")
                time.sleep(10)
                continue
            raise
        except Exception as e:
            # 一般异常处理
            print(f"登录过程中发生异常: {str(e)}")

            # 检查页面是否已关闭
            if "Target page, context or browser has been closed" not in str(e):
                # 检查页面状态
                try:
                    # 快速检查登录状态
                    current_url = page.url
                    url_changed = login_url != current_url and "/login" not in current_url

                    try:
                        login_form_exists = page.locator('form input[type="password"]').count() > 0
                        page_content = page.content().lower()
                        client_area_indicators = ["client area", "客户中心", "用户中心", "控制面板", "dashboard", "account"]
                        content_indicates_success = any(indicator in page_content for indicator in client_area_indicators)

                        # 如果URL已改变或页面内容表明登录成功，且没有登录表单，则认为登录成功
                        if (url_changed or content_indicates_success) and not login_form_exists:
                            print(f"虽然发生错误，但检测到登录成功")
                            return context, None, None
                    except Exception:
                        pass
                except Exception:
                    pass

            print(f"账号 {account['username']} 登录失败: {str(e)}")

            if attempt < max_retries - 1:
                print(f"等待10秒后重试...")
                time.sleep(10)
                continue
            raise
        finally:
            # 关闭页面
            try:
                page.close()
            except Exception:
                pass

# 检查登录是否成功
def check_login_success(page, login_url):
    """检查是否登录成功"""
    try:
        current_url = page.url
        # 检查URL是否已经改变且不再是登录页面
        url_changed = login_url != current_url and "/login" not in current_url

        # 检查页面内容是否包含客户区域特征
        page_content = page.content().lower()
        client_area_indicators = [
            "client area", "客户中心", "用户中心", "控制面板",
            "hosting plans", "support tickets", "active domains",
            "free plan warning", "dashboard", "account"
        ]
        content_indicates_success = any(indicator.lower() in page_content for indicator in client_area_indicators)

        # 检查是否仍有登录表单
        login_form_exists = page.locator('form input[type="password"]').count() > 0

        # 如果URL已改变或页面内容表明登录成功，且没有登录表单，则认为登录成功
        if (url_changed or content_indicates_success) and not login_form_exists:
            if url_changed:
                print(f"URL已改变: {current_url}")
            if content_indicates_success:
                print(f"页面内容包含客户区域特征")
            return True
    except Exception as e:
        print(f"检查登录状态时出错: {str(e)}")
    return False

# 处理弹窗中的续期按钮
def handle_popup_renew(page, account):
    """处理可能出现的弹窗中的续期按钮"""
    print("检查是否有弹窗续期按钮")

    # 查找可能的弹窗元素
    popup_selectors = [
        '.modal-dialog',
        '.modal-content',
        '.popup',
        '.dialog',
        'div[role="dialog"]',
        '.modal.show',
        '.layui-layer',
        '.layui-layer-content'
    ]

    popup_found = False
    for selector in popup_selectors:
        selector_count = page.locator(selector).count()

        if selector_count > 0:
            popup_found = True

            # 在弹窗中查找续期按钮
            popup_renew_selectors = [
                'button#submitRenew',  # 特定ID
                'button:has-text("点击续费")',  # 特定文本
                'button:has-text("续期")',
                'a:has-text("续期")',
                'button:has-text("续费")',
                'a:has-text("续费")',
                'button:has-text("确定")',
                'button:has-text("确认")',
                'button.btn-primary',
                'button.btn-success',
                'button[type="submit"]',
                'input[type="submit"]'
            ]

            # 尝试点击弹窗中的续期按钮
            popup_button_found = False

            # 首先通过选择器查找
            for btn_selector in popup_renew_selectors:
                full_selector = f"{selector} {btn_selector}"
                btn_count = page.locator(full_selector).count()

                if btn_count > 0:

                    try:
                        # 尝试使用JavaScript点击
                        page.evaluate(f'document.querySelector("{full_selector}").click()')
                        print("使用JavaScript点击弹窗中的续期按钮")
                    except Exception as e:
                        print(f"JavaScript点击弹窗按钮失败: {str(e)}")
                        # 如果JavaScript点击失败，使用Playwright点击
                        page.locator(full_selector).first.click()
                        print("使用Playwright点击弹窗中的续期按钮")

                    popup_button_found = True
                    time.sleep(3)
                    print("点击弹窗中的续期按钮后")
                    break

            # 如果通过选择器未找到按钮，尝试更全面的方法查找
            if not popup_button_found:

                # 在弹窗中查找所有按钮的文本内容
                popup_buttons = page.locator(f"{selector} button").all()
                for button in popup_buttons:
                    try:
                        text = button.text_content().strip()

                        if '续费' in text or '续期' in text or '确定' in text or '确认' in text or '点击续费' in text:

                            button.click()
                            popup_button_found = True
                            time.sleep(3)
                            print("点击弹窗文本匹配按钮后")
                            break
                    except Exception as e:
                        print(f"检查弹窗按钮文本时出错: {str(e)}")

            if popup_button_found:
                print("成功处理弹窗中的按钮")
                return True
            else:
                print("未找到弹窗中的可点击按钮")

    if not popup_found:
        print("未找到弹窗元素")

    return False

def renew_vps(account, context, cookie, cf_clearance_cookie=None, max_retries=2):
    page = context.new_page()

    try:
        for attempt in range(max_retries):
            try:
                # 导航到服务器列表页面
                print(f"尝试 {attempt + 1}/{max_retries}: 导航到 {account['site']}/server/lxc 页面...")
                page.goto(f"{account['site']}/server/lxc", wait_until='networkidle', timeout=12000)  # 使用networkidle等待所有网络请求完成

                # 等待页面完全加载，处理可能的CloudFlare挑战
                print(f"等待5秒，确保页面完全加载并处理CloudFlare挑战...")
                time.sleep(5)

                # 检查是否遇到CloudFlare挑战页面
                if "Just a moment" in page.content() or "Checking your browser" in page.content():
                    print("检测到CloudFlare挑战页面，等待挑战完成...")
                    # 等待更长时间让CloudFlare挑战完成
                    for _ in range(12):  # 最多等待
                        time.sleep(5)
                        if "Just a moment" not in page.content() and "Checking your browser" not in page.content():
                            print("CloudFlare挑战已完成，继续执行...")
                            break

                    # 如果仍然在CloudFlare页面，尝试刷新
                    if "Just a moment" in page.content() or "Checking your browser" in page.content():
                        print("CloudFlare挑战仍未完成，尝试刷新页面...")
                        page.reload(wait_until='networkidle', timeout=12000)
                        time.sleep(5)

                # 获取续期URL
                renew_url = f"{account['site']}{account['renewApi']}"
                print(f"账号 {account['username']} 的续期URL: {renew_url}")

                # 方法1: 直接访问续期页面并点击续期按钮
                try:
<<<<<<< HEAD
                    print(f"方法1: 直接访问续期页面 {renew_url}")

                    page.goto(renew_url, wait_until='networkidle', timeout=12000)
=======
                    debug_info(f"方法1: 直接访问续期页面 {renew_url}", account=account)

                    # 保存续期前的页面内容和截图
                    debug_info("续期前页面状态", data=page.content(), screenshot=page, account=account)

                    page.goto(renew_url, wait_until='networkidle', timeout=120000)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

                    # 等待页面加载
                    time.sleep(5)

                    # 保存导航后的页面内容和截图
                    debug_info("续期页面导航后状态", data=page.content(), screenshot=page, account=account)

                    # 检查是否遇到CloudFlare挑战页面
<<<<<<< HEAD
                    if "Just a moment" in page.content() or "Checking your browser" in page.content():
                        print("续期页面遇到CloudFlare挑战，等待挑战完成...")
=======
                    if page.content().find("Just a moment") > -1 or page.content().find("Checking your browser") > -1:
                        debug_info("续期页面遇到CloudFlare挑战，等待挑战完成...", screenshot=page, account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
                        # 等待更长时间让CloudFlare挑战完成
                        for _ in range(12):  # 最多等待30秒
                            time.sleep(5)
<<<<<<< HEAD
                            if "Just a moment" not in page.content() and "Checking your browser" not in page.content():
                                print("CloudFlare挑战已完成，继续执行...")
=======
                            if page.content().find("Just a moment") == -1 and page.content().find("Checking your browser") == -1:
                                debug_info("CloudFlare挑战已完成，继续执行...", screenshot=page, account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
                                break

                    # 查找并点击续期按钮
                    renew_button_found = False

                    # 使用更简洁的选择器策略
                    selectors = [
                        # 首先尝试特定ID和文本
                        'button#submitRenew',  # 特定ID（大写R）
                        'button#submitrenew',  # 特定ID（小写r，以防万一）
                        'button:has-text("点击续费")',  # 特定文本

                        # 然后尝试通用的提交按钮
                        'button[type="submit"]',  # 通用提交按钮
                        'button.btn-primary',  # 主要按钮

                        # 然后尝试包含特定文本的按钮
                        'button:has-text("续期")',
                        'button:has-text("续费")',
                        'button:has-text("延期")',
                        'button:has-text("增加时长")',

                        # 最后尝试链接
                        'a:has-text("续期")',
                        'a:has-text("续费")',
                        'a:has-text("延期")',
                        'a:has-text("增加时长")'
                    ]

<<<<<<< HEAD
                    # 不再记录所有可见元素

                    # 不再添加重复的选择器

                    for selector in selectors:
                        button_count = page.locator(selector).count()

                        if button_count > 0:
                            print(f"找到续期按钮: {selector}")
=======
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
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

                            try:
                                # 尝试使用JavaScript点击
                                page.evaluate(f'document.querySelector("{selector}").click()')
<<<<<<< HEAD
                                print("使用JavaScript点击续期按钮")
                            except Exception as e:
                                print(f"JavaScript点击失败: {str(e)}")
                                # 如果JavaScript点击失败，使用Playwright点击
                                page.locator(selector).first.click()
                                print("使用Playwright点击续期按钮")
=======
                                debug_info("使用JavaScript点击续期按钮", account=account)
                            except:
                                # 如果JavaScript点击失败，使用Playwright点击
                                page.locator(selector).first.click()
                                debug_info("使用Playwright点击续期按钮", account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

                            renew_button_found = True
                            # 等待页面响应
                            time.sleep(3)
<<<<<<< HEAD
                            print("点击续期按钮后，检查是否出现弹窗")

                            # 检查是否出现弹窗，并处理弹窗中的续期按钮
                            popup_handled = handle_popup_renew(page, account)
                            if popup_handled:
                                print("已处理弹窗中的续期按钮")
                            else:
                                print("未检测到弹窗或弹窗处理失败")

=======
                            # 点击后截图
                            debug_info("点击续期按钮后", screenshot=page, account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
                            break

                    # 如果通过选择器未找到按钮，尝试更全面的方法查找
                    if not renew_button_found:
<<<<<<< HEAD

                        # 1. 检查所有按钮的文本内容
                        debug_info("1. 检查所有按钮的文本内容", account=account)
                        buttons = page.locator('button').all()
                        for button in buttons:
                            try:
                                text = button.text_content().strip()
                                debug_info(f"检查按钮文本: '{text}'", account=account, step_name="check_button_text")
                                if '续费' in text or '续期' in text or '点击续费' in text:
                                    button.click()
                                    renew_button_found = True
                                    time.sleep(3)
                                    debug_info("点击文本匹配的按钮后", account=account, step_name="after_text_click")
                                    break
                            except Exception as e:
                                debug_info(f"检查按钮文本时出错: {str(e)}", account=account, step_name="text_check_error")

                        # 2. 如果仍未找到，检查所有按钮的ID和类
                        if not renew_button_found:
                            debug_info("2. 检查所有按钮的ID和类", account=account)
                            try:
                                # 使用JavaScript获取所有按钮的ID和类
                                button_attrs = page.evaluate('''() => {
                                    const buttons = Array.from(document.querySelectorAll('button'));
                                    return buttons.map(btn => ({
                                        id: btn.id,
                                        class: btn.className,
                                        type: btn.type,
                                        text: btn.textContent.trim(),
                                        dataAttrs: Object.keys(btn.dataset).map(key => `data-${key}=${btn.dataset[key]}`)
                                    }));
                                }''')

                                debug_info(f"页面上的按钮属性: {button_attrs}", account=account)

                                # 查找包含"renew"、"submit"等关键词的按钮
                                for i, attrs in enumerate(button_attrs):
                                    btn_id = attrs.get('id', '').lower()
                                    btn_class = attrs.get('class', '').lower()
                                    btn_text = attrs.get('text', '').lower()
                                    btn_data = ' '.join(attrs.get('dataAttrs', [])).lower()

                                    if ('renew' in btn_id or 'submit' in btn_id or
                                        'renew' in btn_class or 'submit' in btn_class or
                                        '续费' in btn_text or '续期' in btn_text or '点击续费' in btn_text or
                                        'renew' in btn_data or '续费' in btn_data):

                                        debug_info(f"通过属性找到可能的续期按钮: {attrs}", account=account)
                                        # 使用JavaScript点击这个按钮
                                        page.evaluate(f'document.querySelectorAll("button")[{i}].click()')
                                        renew_button_found = True
                                        time.sleep(3)
                                        debug_info("点击属性匹配的按钮后", account=account)
                                        break
                            except Exception as e:
                                debug_info(f"检查按钮属性时出错: {str(e)}", account=account)

                        # 3. 如果仍未找到，尝试直接点击submitRenew按钮
                        if not renew_button_found:
                            debug_info("3. 尝试直接点击submitRenew按钮", account=account)
                            try:
                                # 尝试直接使用JavaScript查找并点击submitRenew按钮
                                clicked = page.evaluate('''() => {
                                    // 尝试多种可能的ID
                                    const ids = ['submitRenew', 'submitrenew', 'submit-renew', 'btnRenew', 'btnSubmit'];
                                    for (const id of ids) {
                                        const btn = document.getElementById(id);
                                        if (btn) {
                                            btn.click();
                                            return true;
                                        }
                                    }

                                    // 尝试查找包含特定文本的按钮
                                    const buttons = Array.from(document.querySelectorAll('button'));
                                    for (const btn of buttons) {
                                        if (btn.textContent.includes('续费') ||
                                            btn.textContent.includes('续期') ||
                                            btn.textContent.includes('点击续费')) {
                                            btn.click();
                                            return true;
                                        }
                                    }

                                    return false;
                                }''')

                                if clicked:
                                    debug_info("通过JavaScript直接点击了续期按钮", account=account)
                                    renew_button_found = True
                                    time.sleep(3)
                                else:
                                    debug_info("无法通过JavaScript直接点击续期按钮", account=account)
                            except Exception as e:
                                debug_info(f"直接点击submitRenew按钮时出错: {str(e)}", account=account)

                        # 检查是否出现弹窗
                        if renew_button_found:
                            popup_handled = handle_popup_renew(page, account)
                            if popup_handled:
                                debug_info("已处理弹窗中的续期按钮", account=account, step_name="popup_handled_after_search")

                    if not renew_button_found:
                        debug_info("未找到续期按钮，尝试方法2...", account=account, step_name="no_button_found")
=======
                        debug_info("未找到续期按钮，尝试方法2...", screenshot=page, account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
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
<<<<<<< HEAD
=======
                            debug_info(f"找到确认按钮: {selector}", screenshot=page, account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

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
<<<<<<< HEAD
                            debug_info("点击确认按钮后", account=account)
                            break

                    if confirm_button_found:
                        print("已点击确认按钮")
                    else:
                        print("未找到确认按钮")
=======
                            debug_info("点击确认按钮后", screenshot=page, account=account)
                            break

                    if confirm_button_found:
                        debug_info("已点击确认按钮", account=account)
                    else:
                        debug_info("未找到确认按钮", account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

                    # 检查续期结果
                    success_texts = ["续期成功", "已续期", "操作成功", "success"]
                    page_content = page.content().lower()

                    # 保存最终页面内容
                    debug_info("续期操作后页面内容", data=page_content, account=account)

<<<<<<< HEAD
                    # 尝试从页面内容中提取JSON响应或消息
                    try:
                        # 导入re模块
                        import re
                        # 首先尝试查找layui-layer-content中的消息（基于调试日志中发现的结构）
                        layui_msg_pattern = r'<div[^>]*class="layui-layer-content[^"]*"[^>]*>(.*?)</div>'
                        layui_msg_match = re.search(layui_msg_pattern, page_content, re.DOTALL)

                        if layui_msg_match:
                            # 提取消息内容，去除HTML标签
                            msg_html = layui_msg_match.group(1)
                            msg_text = re.sub(r'<[^>]*>', '', msg_html).strip()
                            debug_info(f"找到弹窗消息: {msg_text}", account=account)

                            # 检查消息内容是否包含特定文本
                            if "请在到期前" in msg_text and "天后再续费" in msg_text:
                                debug_info(f"续期结果: {msg_text}", account=account)
                                return {"code": 1, "msg": msg_text, "success": True}
                            elif "续期成功" in msg_text or "续费成功" in msg_text or "操作成功" in msg_text:
                                debug_info(f"续期成功: {msg_text}", account=account)
                                return {"code": 0, "msg": msg_text, "success": True}
                            else:
                                debug_info(f"续期结果: {msg_text}", account=account)
                                return {"code": 1, "msg": msg_text, "success": True}

                        # 如果没有找到layui消息，尝试查找JSON格式的响应
                        json_pattern = r'({[\s\S]*?"code"[\s\S]*?"msg"[\s\S]*?})'
                        json_match = re.search(json_pattern, page_content)

                        if json_match:
                            response_text = json_match.group(1)
                            debug_info(f"找到JSON响应: {response_text}", account=account)

                            try:
                                response_json = json.loads(response_text)
                                code = response_json.get('code', None)
                                msg = response_json.get('msg', '')

                                # 检查code是否为0或1（通常0表示成功，1可能表示部分成功或特殊情况）
                                if code == 0 or code == 1:
                                    debug_info(f"API续期成功: code: {code}, msg: {msg}", account=account)
                                    return {"code": code, "msg": msg, "success": True}
                                else:
                                    debug_info(f"API响应状态码非0或1: code: {code}, msg: {msg}", account=account)
                                    # 尝试导航到续期页面查看结果
                                    try:
                                        page.goto(renew_url, wait_until='networkidle', timeout=12000)
                                        debug_info("续期后页面状态", account=account)
                                    except:
                                        pass

                                    return {"code": code, "msg": msg, "success": False}
                            except json.JSONDecodeError:
                                debug_info(f"无法解析JSON响应: {response_text}", account=account)

                        # 尝试查找alert消息
                        alert_pattern = r'alert\([\'"]([^\'"]*?)[\'"]\)'
                        alert_match = re.search(alert_pattern, page_content)

                        if alert_match:
                            alert_text = alert_match.group(1)
                            debug_info(f"找到alert消息: {alert_text}", account=account)
                            return {"code": 1, "msg": alert_text, "success": True}

                    except Exception as e:
                        debug_info(f"提取响应消息时出错: {str(e)}", account=account)

                    # 如果无法提取JSON，使用传统方法检查成功文本
=======
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
                    success = False
                    for text in success_texts:
                        if text.lower() in page_content:
                            success = True
                            debug_info(f"检测到成功信息: '{text}'", account=account)
                            break

                    if success:
<<<<<<< HEAD
                        debug_info("续期成功", account=account)
                        return {"success": True, "text": "续期成功"}
                    else:
                        # 如果页面上没有成功信息，尝试方法2
                        debug_info("未检测到续期成功信息，尝试方法2...", account=account)
=======
                        debug_info("续期成功", screenshot=page, account=account)
                        return "续期成功"
                    else:
                        # 如果页面上没有成功信息，尝试方法2
                        debug_info("未检测到续期成功信息，尝试方法2...", screenshot=page, account=account)
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
                        raise Exception("未检测到续期成功信息")

                except Exception as e:
                    debug_info(f"方法1失败: {str(e)}，尝试方法2...", account=account)
                    # 保存异常堆栈信息
                    debug_info("方法1失败详细信息", data=traceback.format_exc(), account=account)

                # 方法2: 使用API请求续期（暂时禁用，但保留代码以便于调试）
                try:
<<<<<<< HEAD
                    print(f"方法2: API续期功能已暂时禁用，仅测试按钮点击续期")
                    # 返回一个模拟的成功结果，使用与方法1相同的返回格式
                    return {"success": True, "text": "按钮点击续期测试完成，API续期功能已暂时禁用"}

                except Exception as e:
                    print(f"方法2失败: {str(e)}")

                    # 如果方法2也失败，尝试重试
=======
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

>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84
                    if attempt < max_retries - 1:
                        debug_info(f"等待5秒后重试...", account=account)
                        time.sleep(5)
                        continue
                    raise


            except Exception as e:
<<<<<<< HEAD
                print(f"续期尝试 {attempt + 1} 失败: {str(e)}")
=======
                debug_info(f"续期尝试 {attempt + 1} 失败: {str(e)}", account=account)
                # 保存异常堆栈信息
                debug_info("续期失败详细信息", data=traceback.format_exc(), account=account)
                # 保存当前页面状态
                try:
                    debug_info("续期失败时页面状态", screenshot=page, account=account)
                except:
                    pass
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

                if attempt < max_retries - 1:
                    debug_info(f"等待5秒后重试...", account=account)
                    time.sleep(5)
                    continue
                raise
        # 如果所有尝试都失败，抛出异常
        raise Exception(f"所有 {max_retries} 次续期尝试都失败")
    finally:
        # 检查页面是否仍然可用
        try:
            # 尝试访问页面的URL属性，如果页面已关闭会抛出异常
            _ = page.url
        except Exception:
            pass

        # 截图完成后再关闭页面（如果尚未关闭）
        try:
            page.close()
        except Exception:
            # 页面可能已经关闭，忽略错误
            pass

def main():
<<<<<<< HEAD
    # 记录启动信息
    print(f"NetKeep启动 - 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 从环境变量加载账号信息
    netkeep_accounts_env = os.environ.get('NETKEEP_ACCOUNTS', '[]')

    # 不再记录环境变量值
=======
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
>>>>>>> fd135d5c62be0fdec01deded7e5f90adbd75aa84

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
        # 不再需要need_cookie变量

        if need_renew:
            print(f"账号 {i+1}: {account['username']} ({site_name}), 需要续期, 续期API: {account['renewApi']}")
        else:
            print(f"账号 {i+1}: {account['username']} ({site_name}), 仅登录")



    if not accounts:
        print("NETKEEP_ACCOUNTS 环境变量中未配置任何账号")
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
                print(f"仅登录")
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
                # 不再需要need_cookie变量

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

                    # 处理续期结果
                    if isinstance(result, dict):
                        # 如果结果是字典格式
                        if 'code' in result and 'msg' in result:
                            # API响应格式
                            code = result.get('code')
                            msg = result.get('msg', '')
                            success = result.get('success', False)

                            if success:
                                renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期成功: code: {code}, msg: \"{msg}\"")
                            else:
                                renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期结果: code: {code}, msg: \"{msg}\"")
                        elif 'text' in result:
                            # 文本响应格式
                            text = result.get('text', '')
                            success = result.get('success', False)

                            if success:
                                renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期成功: {text}")
                            else:
                                renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期结果: {text}")
                        else:
                            # 其他字典格式
                            result_readable = json.dumps(result, ensure_ascii=False)
                            renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期结果: {result_readable}")
                    else:
                        # 如果结果是字符串或其他格式
                        try:
                            # 尝试解析为JSON
                            result_json = json.loads(result)
                            if 'msg' in result_json:
                                # 确保Unicode已经被正确解码为中文
                                result_json['msg'] = result_json['msg']
                                result_readable = json.dumps(result_json, ensure_ascii=False)
                            else:
                                result_readable = str(result)
                        except:
                            result_readable = str(result)

                        renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期结果: {result_readable}")

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
