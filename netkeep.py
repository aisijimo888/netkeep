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
    env_example_path = '.env.example'
    print("环境变量NETKEEP_ACCOUNTS:", os.environ.get('NETKEEP_ACCOUNTS', '未设置'))

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

def login_and_get_cookie(account, browser, max_retries=2):  # 减少重试次数为2次
    # 检查是否需要获取Cookie
    # 如果没有renewApi字段，默认不需要获取Cookie
    need_cookie = account.get('needCookie', 'renewApi' in account)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
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

                # 返回context、page、cookie和cf_clearance_cookie
                return context, page, cookie_value, cf_clearance_cookie
            else:
                # 不需要获取Cookie，只需登录
                print(f"账号 {account['username']} 登录成功，不需要获取Cookie")
                # 返回context、page、None和None
                return context, page, None, None
        except PlaywrightTimeoutError as e:
            print(f"账号 {account['username']} 登录尝试 {attempt + 1} 失败: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
        except Exception as e:
            print(f"账号 {account['username']} 登录失败: {str(e)}")
            raise

def renew_vps(account, context, page, cookie, cf_clearance_cookie=None, max_retries=2):  # 减少重试次数为2次
    """在登录成功的同一个页面中执行续期操作"""
    try:
        for attempt in range(max_retries):
            try:
                # 导航到续期页面
                renew_url = f"{account['site']}{account['renewApi']}"
                print(f"尝试 {attempt + 1}/{max_retries}: 导航到 {renew_url} 页面...")

                # 直接在当前页面中导航到续期URL
                page.goto(renew_url, wait_until='load', timeout=120000)

                # 等待一段时间，确保页面加载完成
                print(f"等待3秒，确保页面加载完成...")
                time.sleep(3)

                # 获取页面内容
                content = page.content()

                # 打印页面内容以便调试
                print(f"账号 {account['username']} 续期页面内容: {content[:400]}...")

                # 检查页面内容，判断是否续期成功
                if "成功" in content or "success" in content.lower():
                    print(f"账号 {account['username']} 续期成功")
                    return content

                # 尝试使用Playwright的内置请求功能
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

                # 如果API请求失败，尝试查找并点击续期按钮
                try:
                    # 尝试查找并点击提交按钮
                    submit_button = page.query_selector('button[type="submit"]')
                    if submit_button:
                        submit_button.click()
                        page.wait_for_load_state('load', timeout=120000)
                        time.sleep(3)

                        # 再次检查页面内容
                        content = page.content()
                        if "成功" in content or "success" in content.lower():
                            print(f"账号 {account['username']} 续期成功")
                            return content
                except Exception as e:
                    print(f"尝试点击提交按钮失败: {str(e)}")

                # 如果仍然失败，尝试使用JavaScript提交表单
                try:
                    result = page.evaluate('''() => {
                        const form = document.querySelector('form');
                        if (form) {
                            form.submit();
                            return "表单已提交";
                        }
                        return "未找到表单";
                    }''')
                    print(f"JavaScript提交表单结果: {result}")

                    page.wait_for_load_state('load', timeout=120000)
                    time.sleep(3)

                    # 再次检查页面内容
                    content = page.content()
                    if "成功" in content or "success" in content.lower():
                        print(f"账号 {account['username']} 续期成功")
                        return content
                except Exception as e:
                    print(f"尝试使用JavaScript提交表单失败: {str(e)}")

                # 如果所有尝试都失败，检查是否需要重试
                if attempt < max_retries - 1:
                    print(f"续期尝试 {attempt + 1} 失败，将在5秒后重试...")
                    time.sleep(5)
                    continue
                else:
                    print(f"所有续期尝试都失败，返回最后一次尝试的页面内容")
                    return content
            except Exception as e:
                print(f"续期尝试 {attempt + 1} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    print(f"等待5秒后重试...")
                    time.sleep(5)
                    continue
                raise
        # 如果所有尝试都失败，抛出异常
        raise Exception(f"所有 {max_retries} 次续期尝试都失败")
    except Exception as e:
        print(f"续期过程中出错: {str(e)}")
        raise

def main():
    # 从环境变量加载账号信息
    # 兼容旧的FREECLOUD_ACCOUNTS变量名
    netkeep_accounts_env = os.environ.get('NETKEEP_ACCOUNTS', os.environ.get('FREECLOUD_ACCOUNTS', '[]'))

    # 打印原始环境变量值，用于调试
    print("原始NETKEEP_ACCOUNTS环境变量值:", netkeep_accounts_env)

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
                browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])

                # 登录
                context, page, cookie, cf_clearance_cookie = login_and_get_cookie(account, browser)
                login_statuses.append(f"账号 {account['username']} ({site_name}) 登录成功")

                # 检查是否需要续期
                if need_renew:
                    # 确保有Cookie
                    if not cookie:
                        raise Exception("需要续期但未获取到Cookie")

                    print(f"账号 {account['username']} 配置了续期API，执行续期操作...")

                    # 使用Playwright的内置请求功能发送续期请求
                    try:
                        result = renew_vps(account, context, page, cookie, cf_clearance_cookie)

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
                    except Exception as e:
                        print(f"使用Playwright续期失败: {str(e)}")
                        print("尝试使用备用方法续期...")

                        # 如果Playwright方法失败，尝试使用备用方法
                        try:
                            # 尝试直接在当前页面中导航到续期URL
                            renew_url = f"{account['site']}{account['renewApi']}"
                            print(f"备用方法：直接导航到 {renew_url}")

                            # 直接在当前页面中导航到续期URL
                            page.goto(renew_url, wait_until='load', timeout=120000)

                            # 等待一段时间，确保页面加载完成
                            time.sleep(3)

                            # 获取页面内容
                            content = page.content()

                            # 检查页面内容，判断是否续期成功
                            if "成功" in content or "success" in content.lower():
                                print(f"账号 {account['username']} 续期成功")
                                result = content
                                result_readable = "页面内容显示续期成功"
                                renew_statuses.append(f"账号 {account['username']} ({site_name}) 续期成功: {result_readable}")
                                print(f"账号 {account['username']} 续期完成")
                                return

                            # 如果直接导航失败，尝试使用requests发送请求
                            print("直接导航未成功，尝试使用requests发送请求...")

                            # 设置请求头
                            headers = {
                                'Cookie': cookie,
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                                'Referer': f"{account['site']}/server/lxc",
                                'Accept': 'application/json, text/javascript, */*; q=0.01',
                                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                                'X-Requested-With': 'XMLHttpRequest',
                                'Origin': account['site'],
                                'Connection': 'keep-alive',
                                'Sec-Fetch-Dest': 'empty',
                                'Sec-Fetch-Mode': 'cors',
                                'Sec-Fetch-Site': 'same-origin',
                                'Pragma': 'no-cache',
                                'Cache-Control': 'no-cache'
                            }

                            # 如果有cf_clearance_cookie，添加到Cookie中
                            if cf_clearance_cookie:
                                headers['Cookie'] += f"; cf_clearance={cf_clearance_cookie['value']}"

                            # 发送续期请求
                            response = requests.get(renew_url, headers=headers)

                            # 检查响应状态码
                            if response.status_code == 200:
                                result = response.text

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
                                raise Exception(f"续期请求失败，状态码: {response.status_code}")
                        except Exception as e2:
                            print(f"备用续期方法也失败: {str(e2)}")
                            raise Exception(f"所有续期方法都失败: {str(e)}, {str(e2)}")
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
                    # 不需要单独关闭page，因为关闭context会自动关闭所有相关页面
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
