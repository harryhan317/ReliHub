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
    print(f"第一次点击'我的'菜单，注册提示页是否显示: {modal_visible}")

    if modal_visible:
        # 检查模态框尺寸
        modal_content = page.locator('.modal-content')
        if modal_content.count() > 0:
            transform = modal_content.evaluate('el => getComputedStyle(el).transform')
            max_height = modal_content.evaluate('el => getComputedStyle(el).maxHeight')
            max_width = modal_content.evaluate('el => getComputedStyle(el).maxWidth')
            print(f"模态框尺寸 - transform: {transform}, max-height: {max_height}, max-width: {max_width}")

        # 点击"返回继续浏览"
        page.locator('text=返回继续浏览').click()
        page.wait_for_timeout(500)

        # 再次点击"我的"导航菜单
        page.locator('text=我的').click()
        page.wait_for_timeout(500)

        # 检查是否再次弹出注册提示页
        modal_visible_again = page.locator('text=注册解锁完整功能').is_visible()
        print(f"第二次点击'我的'菜单，注册提示页是否显示: {modal_visible_again}")

        if modal_visible_again:
            print("✅ 修复成功：点击'返回继续浏览'后可以重新弹出提示页")
        else:
            print("❌ 修复失败：点击'返回继续浏览'后无法重新弹出提示页")

    # 截图保存
    page.screenshot(path='/tmp/guest_modal_test.png', full_page=True)

    browser.close()
    print("测试完成，截图保存到 /tmp/guest_modal_test.png")