from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def fetch_rendered_page_and_done(chromedriver_path, url):
    """
    对目标项目第一个 build 失败的按钮的及其前面紧邻的时间进行提取
    """
    # 1. Chrome 配置
    opts = Options()
    # opts.add_argument("--headless")
    opts.add_argument("--enable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    )
    opts.add_argument("--window-size=1200,900")
    # 在函数开头添加时间戳生成（如果尚未添加）
    timestamp = int(time.time())
    driver = webdriver.Chrome(service=Service(chromedriver_path), options=opts)
    try:
        driver.get(url)
        # 等待 build-status 出现并异步加载完毕
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "build-status"))
        )
        time.sleep(10)

        # —— 递归展开所有 shadowRoot
        driver.execute_script("""
                    function expandShadowRoots(root) {
                        root.querySelectorAll('*').forEach(el => {
                            if (el.shadowRoot) {
                                const container = document.createElement('div');
                                container.className = '__shadow_contents';
                                container.innerHTML = el.shadowRoot.innerHTML;
                                el.appendChild(container);
                                expandShadowRoots(container);
                            }
                        });
                    }
                    // 从 document.body 开始
                    expandShadowRoots(document.body);
                """)

        # 1. 获取初始HTML内容（展平前）并保存
        initial_html = driver.page_source

        # 第一次展平Shadow DOM
        start = time.time()

        with open(f"initial.html", "w", encoding="utf-8") as f:
            f.write(initial_html)
        print(f"💾 已保存初始HTML: initial.html")
        # 3. 直接通过Shadow DOM定位第一个按钮并点击
        print("🖱️ 定位并点击第一个按钮...")

        # 定位宿主元素（build-status）
        build_status = driver.execute_script("""
            return document.querySelector('build-status');
        """)

        # 替换原来的按钮定位和点击代码
        print("🖱️ 定位并点击第一个按钮...")

        # 使用单个脚本完成所有操作
        click_success = driver.execute_script("""
            // 1. 查找build-status元素
            const buildStatus = document.querySelector('build-status');
            if (!buildStatus) return false;

            // 2. 进入Shadow DOM
            const shadowRoot = buildStatus.shadowRoot;
            if (!shadowRoot) return false;

            // 3. 查找.buildHistory容器
            const buildHistory = shadowRoot.querySelector('div.buildHistory');
            if (!buildHistory) return false;

            // 4. 查找第一个paper-button
            const firstButton = buildHistory.querySelector('paper-button');
            if (!firstButton) return false;

            // 5. 点击按钮
            firstButton.click();
            return true;
        """)

        if click_success:
            print("✅ 按钮已点击")
        else:
            print("⚠️ 未找到构建历史按钮")
            return None

        # 4. 等待页面响应
        print("⏳ 等待页面响应...")
        time.sleep(5)

        # 5. 重新展平Shadow DOM获取新内容
        print("🔍 重新展平Shadow DOM获取新内容...")
        start = time.time()
        driver.execute_script("""
                    function expandShadowRoots(root) {
                        root.querySelectorAll('*').forEach(el => {
                            if (el.shadowRoot) {
                                const container = document.createElement('div');
                                container.className = '__shadow_contents';
                                container.innerHTML = el.shadowRoot.innerHTML;
                                el.appendChild(container);
                                expandShadowRoots(container);
                            }
                        });
                    }
                    // 从 document.body 开始
                    expandShadowRoots(document.body);
                """)

        # 6. 获取点击后的完整HTML并保存
        rendered_html = driver.page_source
        with open(f"rendered.html", "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"💾 已保存渲染后HTML: rendered.html")
        print("✅ 获取到点击后的HTML内容")

        # 7. 提取特定日志内容
        print("📝 提取日志内容...")
        log_content = ""
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(rendered_html, 'html.parser')

            # 直接定位所有 class="card-content" 的 div
            card_contents = soup.find_all('div', class_='card-content')

            target_pre = None

            # 遍历所有 card-content 元素
            for card_content in card_contents:
                # 获取所有直接子元素
                children = list(card_content.children)

                # 找到最后一个非空子元素
                last_child = None
                for child in reversed(children):
                    if child.name and child.name.strip():  # 确保是有效的标签元素
                        last_child = child
                        break

                # 检查最后一个子元素是否是 pre 标签
                if last_child and last_child.name == 'pre':
                    # 获取文本内容并检查是否以 "starting build" 开头
                    text = last_child.get_text().strip()
                    if text.startswith("starting build"):
                        target_pre = last_child
                        break

            if target_pre:
                log_content = target_pre.get_text()
                print(f"✅ 成功提取日志内容 ({len(log_content)} 字符)")
            else:
                print("⚠️ 未找到符合条件的日志内容")
                # 备选方案：尝试查找包含 "starting build" 的 pre 标签
                starting_build_pre = soup.find('pre', string=lambda t: t and t.strip().startswith("starting build"))
                if starting_build_pre:
                    log_content = starting_build_pre.get_text()
                    print("✅ 通过备选方案找到日志内容")
                else:
                    print("⚠️ 备选方案也未能找到日志内容")

        except Exception as e:
            print(f"❌ 日志提取失败: {str(e)}")
            # 调试：保存解析失败的HTML
            with open("parse_error.html", "w", encoding="utf-8") as f:
                f.write(rendered_html)
            print("💾 已保存解析失败的HTML到 parse_error.html")

        # 8. 保存日志内容到TXT文件
        log_filename = f"build_log.txt"
        try:
            with open(log_filename, "w", encoding="utf-8") as log_file:
                log_file.write(log_content)
            print(f"💾 日志内容已保存到: {log_filename}")
        except Exception as e:
            print(f"❌ 保存日志文件失败: {str(e)}")
            log_filename = None

    finally:
        driver.quit()


if __name__ == "__main__":
    chromedriver_path = r"E:\python_project\OSS\chromedriver\chromedriver-win64\chromedriver.exe"
    test_url = "https://oss-fuzz-build-logs.storage.googleapis.com/index.html#tint"
    fetch_rendered_page_and_done(chromedriver_path, test_url)
