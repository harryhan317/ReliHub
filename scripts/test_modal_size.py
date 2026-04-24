from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()

    # 访问3004端口的Welcome页面
    page.goto('http://localhost:3004/welcome')
    page.wait_for_load_state('networkidle')

    # 清除本地存储，确保是游客状态
    page.evaluate('''() => {
        localStorage.removeItem('relihub_last_visit');
        localStorage.removeItem('relihub_welcome_seen');
        localStorage.removeItem('guest_guide_times');
    }''')
    page.reload()
    page.wait_for_load_state('networkidle')

    # 点击"路过，先来看看"
    page.locator('text=路过，先来看看').click()
    page.wait_for_load_state('networkidle')

    # 等待页面加载完成
    page.wait_for_timeout(1000)

    # 点击"我的"导航菜单
    page.locator('text=我的').click()
    page.wait_for_timeout(500)

    # 检查是否弹出注册提示页
    modal_visible = page.locator('text=注册解锁完整功能').is_visible()
    print(f"注册提示页是否显示: {modal_visible}")

    if modal_visible:
        # 检查模态框尺寸和位置
        modal_content = page.locator('.modal-content')
        if modal_content.count() > 0:
            transform = modal_content.evaluate('el => getComputedStyle(el).transform')
            max_width = modal_content.evaluate('el => getComputedStyle(el).maxWidth')
            width = modal_content.evaluate('el => el.offsetWidth')
            height = modal_content.evaluate('el => el.offsetHeight')
            
            # 获取模态框在视口中的位置
            rect = modal_content.evaluate('el => el.getBoundingClientRect()')
            
            print(f"模态框尺寸 - 实际宽高: {width}px x {height}px")
            print(f"模态框位置 - 左: {rect['x']}px, 上: {rect['y']}px, 右: {rect['x'] + rect['width']}px, 下: {rect['y'] + rect['height']}px")
            print(f"视口尺寸: 390px x 844px")
            print(f"是否在视口内: {rect['x'] >= 0 and rect['x'] + rect['width'] <= 390 and rect['y'] >= 0 and rect['y'] + rect['height'] <= 844}")
            
            # 检查是否超出手机框架
            if rect['x'] >= 0 and rect['x'] + rect['width'] <= 390 and rect['y'] >= 0 and rect['y'] + rect['height'] <= 844:
                print("✅ 尺寸合适：提示页完全在手机框架内")
            else:
                print("❌ 尺寸问题：提示页超出了手机框架")

    # 截图保存
    page.screenshot(path='/tmp/guest_modal_size_test.png', full_page=True)

    browser.close()
    print("测试完成，截图保存到 /tmp/guest_modal_size_test.png")