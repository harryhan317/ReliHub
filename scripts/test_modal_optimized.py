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
            rect = modal_content.evaluate('el => el.getBoundingClientRect()')
            print(f"模态框尺寸 - 宽: {rect['width']}px, 高: {rect['height']}px")
            print(f"模态框位置 - 左: {rect['x']}px, 上: {rect['y']}px")
            
            # 检查提示词是否在一行内显示
            benefit_items = page.locator('.benefit-item')
            for i in range(benefit_items.count()):
                item = benefit_items.nth(i)
                text = item.inner_text()
                is_single_line = item.evaluate('el => el.scrollWidth <= el.offsetWidth')
                print(f"提示词 {i+1}: '{text}' - 是否在一行内: {is_single_line}")
            
            # 计算黄金分割线位置（离底部约0.382比例）
            viewport_height = 844
            golden_ratio_position = viewport_height * 0.382
            benefits_container_rect = page.locator('.register-guide-benefits').evaluate('el => el.getBoundingClientRect()')
            benefits_bottom = benefits_container_rect['y'] + benefits_container_rect['height']
            
            print(f"黄金分割线位置: {golden_ratio_position}px")
            print(f"提示词底部位置: {benefits_bottom}px")
            print(f"是否接近黄金分割线: {abs(benefits_bottom - golden_ratio_position) < 50}")
            
            # 检查整体布局
            if rect['width'] > 320:
                print("✅ 横向尺寸已加大")
            else:
                print("❌ 横向尺寸需要进一步调整")
                
            if rect['height'] < 500:
                print("✅ 纵向尺寸已适当减少")
            else:
                print("❌ 纵向尺寸需要进一步调整")

    # 截图保存
    page.screenshot(path='/tmp/guest_modal_optimized.png', full_page=True)

    browser.close()
    print("测试完成，截图保存到 /tmp/guest_modal_optimized.png")