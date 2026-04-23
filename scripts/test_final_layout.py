#!/usr/bin/env python3
"""测试最终提示页布局效果"""

from playwright.sync_api import sync_playwright
import time

def test_final_layout():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={'width': 390, 'height': 844},
            device_scale_factor=1
        )
        page = context.new_page()
        
        try:
            # 访问欢迎页面
            page.goto('http://localhost:3005/welcome')
            time.sleep(2)
            
            # 点击"路过，先来看看"
            page.click('text=路过，先来看看')
            time.sleep(2)
            
            # 点击"我的"导航菜单
            page.click('text=我的')
            time.sleep(2)
            
            # 检查提示页是否显示
            modal = page.locator('.modal-content')
            if modal.is_visible():
                print("✅ 提示页显示成功")
                
                # 检查更新后的提示词文本
                benefit_items = page.locator('.benefit-item')
                expected_texts = [
                    'AI问答更多对话，专业解答可靠性问题',
                    '更多资源库访问，下载标准与案例',
                    '社区互动，与行业专家交流讨论',
                    '注册即送30可可豆，早鸟额外20可可豆'
                ]
                
                for i in range(4):
                    item = benefit_items.nth(i)
                    if item.is_visible():
                        text = item.text_content().strip()
                        expected = expected_texts[i]
                        if text == expected:
                            print(f"✅ 提示词{i+1}文本正确: {text}")
                        else:
                            print(f"❌ 提示词{i+1}文本错误，期望: {expected}，实际: {text}")
                        
                        # 检查是否在一行内显示
                        if '\n' not in text:
                            print(f"✅ 提示词{i+1}在一行内显示")
                        else:
                            print(f"❌ 提示词{i+1}出现换行")
                
                # 检查按钮是否完全显示
                back_button = page.locator('text=返回继续浏览')
                if back_button.is_visible():
                    button_bounds = back_button.bounding_box()
                    modal_bounds = modal.bounding_box()
                    
                    if button_bounds and modal_bounds:
                        # 检查按钮是否在模态框内
                        button_bottom = button_bounds['y'] + button_bounds['height']
                        modal_bottom = modal_bounds['y'] + modal_bounds['height']
                        
                        if button_bottom <= modal_bottom:
                            print("✅ '返回继续浏览'按钮完全显示在模态框内")
                        else:
                            print(f"❌ '返回继续浏览'按钮部分被截断")
                
                # 检查整体布局
                modal_bounds = modal.bounding_box()
                if modal_bounds:
                    modal_height = modal_bounds['height']
                    modal_top = modal_bounds['y']
                    
                    print(f"📏 模态框高度: {modal_height:.1f}px")
                    print(f"📍 模态框顶部位置: {modal_top:.1f}px")
                    
                    # 检查是否在屏幕内
                    if modal_top >= 0 and modal_top + modal_height <= 844:
                        print("✅ 模态框完全在屏幕内显示")
                    else:
                        print("❌ 模态框超出屏幕范围")
                
                # 截图保存以供检查
                page.screenshot(path='final_modal_layout.png')
                print("📸 截图已保存为 final_modal_layout.png")
                
            else:
                print("❌ 提示页未显示")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    test_final_layout()