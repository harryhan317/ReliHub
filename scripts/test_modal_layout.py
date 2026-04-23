#!/usr/bin/env python3
"""测试提示页布局优化效果"""

from playwright.sync_api import sync_playwright
import time

def test_modal_layout():
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
                
                # 检查提示词是否在一行内显示
                benefit_items = page.locator('.benefit-item')
                for i in range(4):
                    item = benefit_items.nth(i)
                    if item.is_visible():
                        text = item.text_content()
                        # 检查是否出现换行
                        if '\n' in text:
                            print(f"❌ 提示词{i+1}出现换行: {text}")
                        else:
                            print(f"✅ 提示词{i+1}在一行内显示: {text}")
                        
                        # 检查文本是否被截断
                        computed_style = page.evaluate("""(element) => {
                            return {
                                whiteSpace: window.getComputedStyle(element).whiteSpace,
                                overflow: window.getComputedStyle(element).overflow,
                                textOverflow: window.getComputedStyle(element).textOverflow,
                                width: element.offsetWidth,
                                scrollWidth: element.scrollWidth
                            };
                        }""", item.element_handle())
                        
                        if computed_style['scrollWidth'] > computed_style['width']:
                            print(f"⚠️  提示词{i+1}可能被截断: 容器宽度{computed_style['width']}px, 文本宽度{computed_style['scrollWidth']}px")
                        else:
                            print(f"✅ 提示词{i+1}完全显示: 容器宽度{computed_style['width']}px, 文本宽度{computed_style['scrollWidth']}px")
                
                # 检查黄金分割线位置
                modal_bounds = modal.bounding_box()
                benefits_container = page.locator('.register-guide-benefits')
                benefits_bounds = benefits_container.bounding_box()
                
                if modal_bounds and benefits_bounds:
                    modal_height = modal_bounds['height']
                    benefits_top = benefits_bounds['y'] - modal_bounds['y']
                    golden_ratio_position = modal_height * 0.382
                    
                    print(f"📏 模态框高度: {modal_height:.1f}px")
                    print(f"📍 提示词顶部位置: {benefits_top:.1f}px")
                    print(f"🎯 黄金分割线位置: {golden_ratio_position:.1f}px")
                    
                    # 检查是否接近黄金分割线位置（允许±10px误差）
                    if abs(benefits_top - golden_ratio_position) <= 10:
                        print("✅ 提示词位置接近黄金分割线")
                    else:
                        print(f"❌ 提示词位置偏离黄金分割线: 相差{abs(benefits_top - golden_ratio_position):.1f}px")
                
            else:
                print("❌ 提示页未显示")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        finally:
            time.sleep(3)
            browser.close()

if __name__ == "__main__":
    test_modal_layout()