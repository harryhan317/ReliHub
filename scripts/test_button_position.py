#!/usr/bin/env python3
"""测试按钮区域位置变化"""

from playwright.sync_api import sync_playwright
import time

def test_button_position():
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
                
                # 获取模态框和按钮的位置信息
                modal_bounds = modal.bounding_box()
                back_button = page.locator('text=返回继续浏览')
                button_bounds = back_button.bounding_box()
                
                if modal_bounds and button_bounds:
                    modal_height = modal_bounds['height']
                    modal_top = modal_bounds['y']
                    button_bottom = button_bounds['y'] + button_bounds['height']
                    modal_bottom = modal_top + modal_height
                    
                    # 计算按钮距离模态框底部的距离
                    button_to_bottom = modal_bottom - button_bottom
                    
                    print(f"📏 模态框高度: {modal_height:.1f}px")
                    print(f"📍 模态框顶部位置: {modal_top:.1f}px")
                    print(f"📍 模态框底部位置: {modal_bottom:.1f}px")
                    print(f"📍 按钮底部位置: {button_bottom:.1f}px")
                    print(f"📐 按钮距离模态框底部: {button_to_bottom:.1f}px")
                    
                    # 检查按钮是否在模态框内
                    if button_bottom <= modal_bottom:
                        print("✅ 按钮完全在模态框内")
                        
                        # 计算按钮在模态框内的相对位置
                        button_relative_position = (button_bottom - modal_top) / modal_height
                        print(f"📊 按钮在模态框内的相对位置: {button_relative_position:.3f} (从顶部算起)")
                        
                        # 计算距离底部的相对位置
                        distance_from_bottom = 1 - button_relative_position
                        print(f"📊 按钮距离模态框底部的相对位置: {distance_from_bottom:.3f}")
                    
                    # 获取所有按钮的位置
                    buttons = page.locator('.modal-content button')
                    button_count = buttons.count()
                    
                    print(f"\n🔘 按钮数量: {button_count}")
                    for i in range(button_count):
                        button = buttons.nth(i)
                        btn_bounds = button.bounding_box()
                        if btn_bounds:
                            btn_text = button.text_content().strip()
                            btn_top = btn_bounds['y'] - modal_top
                            btn_bottom_rel = (btn_bounds['y'] + btn_bounds['height']) - modal_top
                            print(f"  按钮{i+1} ({btn_text}): 顶部{btn_top:.1f}px, 底部{btn_bottom_rel:.1f}px")
                
            else:
                print("❌ 提示页未显示")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    test_button_position()