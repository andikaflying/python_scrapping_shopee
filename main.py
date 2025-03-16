from flask import Flask, jsonify
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Ensure non-ASCII characters are not escaped
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False 
def extract_shopee_title(driver):
    try:
        title = driver.find_element(By.CSS_SELECTOR, ".two-line-text > span").text
        
        return title
    except Exception as e:
        print(f"Error extracting shopee title: {str(e)}")
        
    return "Title not found"

def extract_shopee_images(driver):
    images = []
    
    try:
        carousel_items = driver.find_elements(By.CSS_SELECTOR, "li.stardust-carousel__item")
        print(f"Found {len(carousel_items)} carousel items")
        
        for item in carousel_items:
            try:
                # Look for image element
                img = item.find_element(By.CSS_SELECTOR, "img")
                
                # Get the direct src if available
                src = img.get_attribute("src")
                if src:
                    images.append(src)
                    continue
                
                # If no direct src, try to get from srcset
                srcset = img.get_attribute("srcset")
                if srcset:
                    # Parse the srcset to get the highest resolution image
                    sizes = srcset.split(",")
                    highest_res = sizes[-1].strip().split(" ")[0]
                    images.append(highest_res)
            except Exception as e:
                print(f"Error extracting image from carousel item: {str(e)}")
    except Exception as e:
        print(f"Error finding carousel items: {str(e)}")
    
    # Remove duplicates while preserving order
    unique_images = []
    for img in images:
        if img and img not in unique_images:
            unique_images.append(img)
    
    print(f"Extracted {len(unique_images)} unique product images")
    return unique_images

def scrape_shopee_product():
    # Setup Chrome WebDriver
    chrome_options = Options()
    # Use this if you want to run headless
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    # Step 1: Go to Shopee login page
    driver.get("https://shopee.tw/buyer/login")
    
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']"))
    )
    
    username_field = driver.find_element(By.CSS_SELECTOR, "input[type='text']")
    username_field.send_keys("andikakurniawan694")
    
    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
    password_field.send_keys("Annisa2001")

    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {
        'headers': {
            "accept": "application/json",
            "accept-language": "en-GB,en;q=0.9,id-ID;q=0.8,id;q=0.7,en-US;q=0.6",
            "af-ac-enc-dat": "562c2ad444a4349c",
            "af-ac-enc-sz-token": "Ek7dbhJOLMIiKq4cSXFDMw==|Pp3znEeMcICAuBXag+f30q1bZLxiTM3Mm789/IWvO8jDJLGvjnd7YgoOjGzKxAL7IZQ94Zv/C8AOa8H015A=|oMEW6t9vUDbveui/|08|3",
            "content-type": "application/json",
            "if-none-match-": "55b03-cb72fe71c780542b58b0250425d63565",
            "priority": "u=1, i",
            "referer": "https://shopee.tw",
            "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            "x-api-source": "pc",
            "x-csrftoken": "RhaI8FXt9m6IBBcPM73VYkNIAAhqqp4c",
            "x-requested-with": "XMLHttpRequest",
            "x-sap-ri": "ea9dd667f37eef5e8db45c3f0501b9ab90edffb2e46412301762",
            "x-sap-sec": "L3pPF9rYGAkum1Awlz5wlaHwHz4LlgAwbz5sljHwbRJrlmRwkRJ/lyAwDA4OljAwDzJplxzw6zJWlmpwrAJzll5wMzIGlYpw5z4Rlb5wLzIFlwAwwz4sljRwezIVljzwWzJ0lYwwfzJAlfRw3RJNlzuwKR5nlwrw/RIMlwRwd546lizwcz5bliuwY5I2lzzwjz5MlZRwU55VlfzwBz4VllRwBR5wlatJTYpwlz5j9l+nNGl+liy6mz5wbzRwlCmo/Uzwlz5mg4IFhR5wtotWeTABcoHw3aH0ub5wlz4CXgjcekAqsZMoYTu5clLyLIFWiVtXl55wRzpwlz5wljVYGiTBlz5+4GBhlGV007QElzRwlz5wlYJfBaYjlz5wlAF4wov5l55wuzrwlz5wlZBHvFk3Xz5wlGAttrXwlz5Yqzrwlz4KcIhNCs4T8zpwlCFlqk/yt0r+8zrwlz5wQlwvN5h4lCn0TJ20CIxul55wazpwlz5wlwDVl55wlz4jkzJ2I9qkJMKr7zpwlz5wPtjulA5wNCevtuUAoRVT/M0x27/BqBtdQgh9PA/LnMjixUY4OZ+/WxV3CtiJ4LFTIwQh8Hb7EB1EBfINjD6D+9VDJlFr7pTHgsVJRZ8rUFeg7neiyDPqFq+BEO8a2rd59TQH3Tl2Pa6CQP2cye1QbY03Yb4uqmYQetoNiaCMBD+6xV17ZTTlFYS4U18aGJKm0eFBlNS3ntp59AlIAFgTMsUKLHdx/8Y4YN+7wMLQmOPRMGvhyPU2pcYSPXtko5XKa5/AkXVzebopFFBfGFYPh24o8tJcAS9I4vGqHtVrWp36pWllYRGxpxY317pYLc1IsEOxxRyejHrK8LxaX7QOgE4UKrnqux1QaUsun96qN5Ebb1LUFz5blz5wd6JqTAAwlz5GLTb4+ju9Zp2YlzJplZzdD9aSysQHm5n2GUChmhygSczlvUSD1Z7PhiPDKuWG6jxUxwwdLTAyVFgWBYbPbKqzdIamjPmDfg+LOaMon5arhjJXBJf8qKXQCHittwNbFafqdRt5UzonCjKxAFWWuXIrgxBCToL21clMwdrOjKtgmmPnduejXPo6tvMwUIxm7snRXqJLqGiGe14avLEhShxPz1AmA0+qsuqzlgYjZz6tjoP3rXNB+DqRyMbpFRjdQBcBw0ZYVpAzahL7XRbUJS1w/CLVUG8eY/RxyMm07HhXCmFwVK/6PjMTUEcuRX+DlsN2og3/IRsyWkbUirMNJfiuOZ8EfcnzybVTphVoO/6vw+nMRInuiGQIT4i0X4tJJ7FL9+pGiEP/TatTsY2Gm/emMZ1pNvmFoGBqJmEmoDWXhAZilCJl10BtoeDAE+aWGweYbG/vaMwxyLYOLEpUilPlKw1u30R56Zx0UGwxhHyjKhZMAdv9T5vqBnGNaCZvzJQ6vj4iKWUrO3XP6kq9YRVPhumtx6GzC/vyfY5k8icVZUI807iSD5OgVUZejgYlE3qy2IsqZZRQm+kAenAS1JEPM924LSvAOibUzRv0blrlU+jaxA5blz5wvoBp/RRwlzJIWlcPlz5wlzHwlzJxVR5wDR5wlaSEm1ovezNf/rXc0Qx6VzcVtAKIXek9aEw9fx15/jArLNqrpkhHXF3eiACcwLdrZZ4iZEyO/NRQL4XV0MJEFmM4fz5wf55wladUbvTJ/AjC291RpIUaXDUIXguwlz5wlz5wlz5wlz5wlz5wlzAwlzJ1Ed1YcpNdTR5wlz5jlz5wGlkKUMHhCMNwlz5wyz5wlYpkD0wtJmigyz5wllRHY8NpvDXolz5wlzAwlzJ49lcetU+9b55wlzI=",
            "x-shopee-language": "en",
            "x-sz-sdk-version": "1.12.17",
        }
    })
    
    login_button = driver.find_element(By.XPATH, "//button[text()='登入']")
    login_button.click()
    time.sleep(5)
    
    # Step 2: Navigate to product page
    list_site = [
        'https://shopee.tw/---i.31188538.19323502897',
        'https://shopee.tw/---i.285438373.23873341214',
        'https://shopee.tw/---i.29982947.11000210471',
        'https://shopee.tw/---i.30988409.2574847807',
        'https://shopee.tw/---i.2976113.26711692578',
        'https://shopee.tw/---i.285438373.23776139571',
        'https://shopee.tw/---i.3694596.1102030853',
        'https://shopee.tw/---i.31414682.20788549419',
        'https://shopee.tw/---i.28944793.1270156956',
        'https://shopee.tw/---i.2806201.25330654951',
        'https://shopee.tw/---i.300988198.23217963746',
        'https://shopee.tw/---i.438866873.24868123469',
        'https://shopee.tw/---i.3770530.24159674644',
        'https://shopee.tw/---i.28876011.20656492126',
        'https://shopee.tw/---i.2752464.2448562484',
        'https://shopee.tw/---i.3092694.888453677',
        'https://shopee.tw/---i.338037348.24636536148',
        'https://shopee.tw/---i.271750671.12523990927',
        'https://shopee.tw/---i.27180751.18465693474',
        'https://shopee.tw/---i.271750671.13823978917',
        'https://shopee.tw/---i.332764831.10490700941',
        'https://shopee.tw/---i.29393503.19517101512',
        'https://shopee.tw/---i.42721645.23554630122',
        'https://shopee.tw/---i.269762955.6438581822',
        'https://shopee.tw/---i.344695970.27100531174',
        'https://shopee.tw/---i.297236004.18432123484',
        'https://shopee.tw/---i.272225913.29656853500',
        'https://shopee.tw/---i.3168173.7338165156',
        'https://shopee.tw/---i.322940809.21361384814',
        'https://shopee.tw/---i.327985547.9368269078',
    ]
    product_list = []
    index = 1

    for site in list_site:
        driver.get(site)
        
        time.sleep(2)
        product_title = ''
        product_images = []
        try:
            product_title = extract_shopee_title(driver)
            product_images = extract_shopee_images(driver)
        except Exception as e:
            print(f"Error extracting data: {str(e)}")
            
            # Save page source for debugging
            with open("page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved page source to page_source.html")

        # Additional data extraction as needed
        product_data = {
            "title": product_title if product_title else "Title not found",
            "images": product_images
        }
        # Take screenshot for debugging
        driver.save_screenshot(f"shopee_page_{index}.png")
        print(f"Saved screenshot to shopee_page_{index}.png")
        index += 1
        
        product_list.append(product_data)
    
    # Close the browser
    driver.quit()
    
    return product_list

@app.route("/scrape", methods=["GET"])
def main():
    try:
        product_info = scrape_shopee_product()
        response = app.response_class(
            response=json.dumps({
                "status": "success",
                "data": product_info,
                "message": "Products retrieved successfully"
            }, ensure_ascii=False),
            status=200,
            mimetype='application/json; charset=utf-8'
        )
        return response
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "data": None
        }), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=True)
