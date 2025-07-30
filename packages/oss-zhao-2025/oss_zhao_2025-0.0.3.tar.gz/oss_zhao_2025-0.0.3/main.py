import time
import re
from datetime import datetime
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_rendered_page(chromedriver_path: str, output_path: str):
    """
    展开所有 shadowRoot，对目标url进行获取
    """
    # 1. Chrome 启动配置
    opts = Options()
    # opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    # 匹配浏览器请求头，模拟真实 Chrome
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    )

    # 2. 指定 chromedriver 可执行文件
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        driver.get("https://oss-fuzz-build-logs.storage.googleapis.com/index.html")

        # 等待 build-status 出现并异步加载完毕
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "build-status"))
        )
        time.sleep(20)

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
        # 5. 获取渲染后的完整 HTML
        rendered_html = driver.page_source

        # 6. 保存到本地文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_html)
        print(f"✅ 渲染后页面已保存到 {output_path}")

    finally:
        driver.quit()


def extract_between_markers(html: str) -> List[str]:
    """
    使用正则表达式从 html 文本中抽取所有外层 <div>…</div> 结构内的项目名，
    仅在该 <div> 内含有 icon="icons:error" 才匹配。
    对每个匹配结果，去掉可能残留的 '/dom-if>' 前缀，只保留真正的项目名。
    """
    pattern = re.compile(
        r'<iron-icon[^>]*icon=["\']icons:error["\'][\s\S]*?</iron-icon>'  # 包含 error 图标
        r'[\s\S]*?'  # 中间任意内容（shadow DOM、dom-if 等）
        r'([^<\s][^<]+?)\s*'  # 捕获非空白开头直到下一个 '<' 之间的文本
        r'</div>',  # 直到外层 </div>
        re.IGNORECASE
    )
    raw = pattern.findall(html)
    cleaned = []
    for m in raw:
        # m 里可能是 "/dom-if>\n                  zip-rs"
        # split by '>'，取最后一段，再 strip 掉前后空白
        name = m.split('>')[-1].strip()
        cleaned.append(name)
    return cleaned


def fetch_and_extract(chromedriver_path: str) -> List[str]:
    """
    启动 Chrome、展平 Shadow DOM、获取页面 HTML，
    并提取所有项目名称对应的url，最后以列表形式返回。
    """
    opts = Options()
    # opts.add_argument("--headless")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
    )

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=opts)
    try:
        driver.get("https://oss-fuzz-build-logs.storage.googleapis.com/index.html")
        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "build-status"))
        )
        time.sleep(20)

        # 展平所有 Shadow DOM
        driver.execute_script("""
            function expand(root) {
                root.querySelectorAll('*').forEach(el => {
                    if (el.shadowRoot) {
                        const c = document.createElement('div');
                        c.className = '__shadow_contents';
                        c.innerHTML = el.shadowRoot.innerHTML;
                        el.appendChild(c);
                        expand(c);
                    }
                });
            }
            expand(document.body);
        """)

        # 获取完整渲染后的 HTML
        rendered_html = driver.page_source

        # 提取并返回所有匹配的片段列表
        return extract_between_markers(rendered_html)

    finally:
        driver.quit()


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

    driver = webdriver.Chrome(service=Service(chromedriver_path), options=opts)
    try:
        driver.get(url)

        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "build-status"))
        )
        time.sleep(20)

        # —— 递归展开所有 shadowRoot（保持你原来的逻辑）
        expand_js = """
        const roots = [];
        document.querySelectorAll('*').forEach(el => {
          if (el.shadowRoot && !el.__expanded) {
            const div = document.createElement('div');
            div.className = '__shadow_contents';
            div.innerHTML = el.shadowRoot.innerHTML;
            el.appendChild(div);
            el.__expanded = true;
            roots.push(el);
          }
        });
        return roots.length;
        """
        start = time.time()
        while True:
            cnt = driver.execute_script(expand_js)
            if cnt == 0 or time.time() - start > 15:
                break
            time.sleep(0.1)

        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8);")
        time.sleep(0.5)
        driver.execute_script(expand_js)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)
        driver.execute_script(expand_js)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(0.5)
        driver.execute_script(expand_js)

        # buttons = driver.find_elements(By.CSS_SELECTOR, "paper-button")
        # 只拿 .buildHistory 下的 <paper-button>
        buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "div.buildHistory paper-button"
        )
        # for button in buttons:
        #     print(button)

        if not buttons:
            print(f"⚠️ 无 <paper-button> 元素，跳过：{url}")
            return None

        ts_pattern = re.compile(r"\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}:\d{2}")
        timestamps = []
        for btn in buttons:
            m = ts_pattern.search(btn.text)
            timestamps.append(m.group() if m else None)
        # for i, timestamp in enumerate(timestamps):
        #     print(i, timestamp)
        note = []
        for i, btn in enumerate(buttons):
            if 'icon="icons:done"' in btn.get_attribute("outerHTML"):
                note.append(1)
            elif 'icon="icons:error"' in btn.get_attribute("outerHTML"):
                note.append(0)
        # for i, btn in enumerate(note):
        #     print(i, btn)
        # print(len(note) - 1, note[len(note) - 1])
        # 进行一个标记数组的整理，将不需要输出的对应下标进行标记
        mark = []
        for i, btn in enumerate(note):
            if i == 0 and note[i] == note[i + 1]:
                mark.append(3)
            elif i == len(note) - 1 and note[i] == note[i - 1]:
                mark.append(3)
            elif note[i] == note[i - 1] and note[i] == note[i + 1]:
                mark.append(3)
            else:
                mark.append(note[i])
        # print("mark:")
        # for i, btn in enumerate(mark):
        #     print(i, btn)
        combined = [(i, timestamps[i], note[i]) for i in range(len(timestamps))]

        # if done_idx is not None:
        #     time2 = timestamps[done_idx]
        #     time1 = timestamps[done_idx - 1] if done_idx > 0 else ""
        #     print(f"✅ {url} -> {time1}, {time2}")
        #     return f"{url},{time1},{time2}"
        # else:
        #     print(f"ℹ️ 未找到 icons:done，跳过：{url}")
        #     return None
        return combined
    finally:
        driver.quit()


if __name__ == "__main__":
    # chromedriver = r"E:\python_project\OSS\chromedriver\chromedriver-win64\chromedriver.exe"
    # # 获取网页html内容
    # output_path = "oss_fuzz_index_with_build_status.html"
    # fetch_rendered_page(chromedriver, output_path)
    # # 获取所有build失败的项目的URL
    # snippets_list = fetch_and_extract(chromedriver)
    # # 获取各个构件失败项目的URL
    # print("抽取到的所有项目拼接url：")
    # project_urls = []
    # base_url = "https://oss-fuzz-build-logs.storage.googleapis.com/index.html#"
    # for idx, snippet in enumerate(snippets_list, 1):
    #     project_urls.append(base_url + snippet)
    #     print(f"{idx}: {base_url + snippet}\n")
    # with open("project_url_list.txt", "w", encoding="utf-8") as f:
    #     for url in project_urls:
    #         f.write(url + "\n")
    # print(f"✅ 已将 {len(project_urls)} 条 URL（保存到 project_url_list.txt")

    # 需要有足够的时间让网页把页面加载出来
    # 对每个URL的build失败的信息进行获取
    chromedriver_path = r"E:\python_project\OSS\chromedriver\chromedriver-win64\chromedriver.exe"
    # 根据当前时间生成文件名，格式：oss_build_YYYYMMDD_HH.txt
    ts = datetime.now().strftime("%Y%m%d_%H")
    output_file = f"oss_build_{ts}.txt"

    # 追加模式打开输出文件
    with open("project_url_list.txt", "r", encoding="utf-8") as fin, \
            open(output_file, "a", encoding="utf-8") as fout:

        for line in fin:
            url = line.strip()
            if not url:
                continue

            result = fetch_rendered_page_and_done(chromedriver_path, url)
            # 输出
            for idx, td, note in result:
                print(idx, td, note)
            # if result:
            #     fout.write(result + "\n")
            #     print(f"✏️ 写入：{result}")

    print(f"✅ 已追加写入所有结果到 {output_file}")
