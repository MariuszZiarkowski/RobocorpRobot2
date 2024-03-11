from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive



@task
def minimal_task():

    """
    
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

        
    order_robots_from_RobotSpareBin()

def order_robots_from_RobotSpareBin():
    open_robot_order_website()
    download_the_orders_files()
    get_orders()
    archive_receipts()
    

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')" )

def open_robot_order_website():
    browser.configure(headless=False)
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_the_orders_files():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders(): 
    library = Tables()
    orders = library.read_table_from_csv(
        "orders.csv", columns= ["Order number", "Head", "Body", "Legs", "Address"]
        )
    for robot_order in orders:
        
        fill_the_form(robot_order) 

def fill_the_form(robot_order):
    page = browser.page()
    close_annoying_modal()
    page.fill("#address", robot_order["Address"])
   
    page.select_option("#head", robot_order["Head"])
  
    page.click(f"#id-body-{robot_order['Body']}")
   
    page.fill('[placeholder="Enter the part number for the legs"]', robot_order["Legs"])
    
    take_preview_screenshot(robot_order["Order number"])
    submit_order()
    create_pdf(robot_order['Order number'])
    add_image_to_pdf(robot_order['Order number'])
    go_to_next_order()



def submit_order():
    """Submit the order """
    page = browser.page()
    order_ok = False
    while not order_ok:
        page.click('#order')

        # repeat until no errors are present
        if page.query_selector('.alert-danger') == None:
            order_ok = True


def take_preview_screenshot(order_number):
    """Take a screenshot and save it"""
    page = browser.page()
    page.click('#preview')
    screenshot_path = 'output/screenshots/order_' + order_number + '.png'
    robot_preview = page.query_selector('#robot-preview-image')
    robot_preview.screenshot(path = screenshot_path)
    return screenshot_path

def create_pdf(orderNumber):
    pdf = PDF()
    pdf.html_to_pdf(get_bill_data(),f"output/bills/robot{orderNumber}.pdf")


def get_bill_data():
    page = browser.page()
    bill_data = page.locator("#receipt").inner_html()
    return bill_data

def add_image_to_pdf(orderNumber):
    pdf = PDF()
    pdf.add_files_to_pdf([f"output/screenshots/order_{orderNumber}.png"], f"output/bills/robot{orderNumber}.pdf", True)


def archive_receipts():
    
    arch = Archive()
    arch.archive_folder_with_zip("output/bills", "receipts.zip", exclude="*.png")

def go_to_next_order():
    page = browser.page()
    page.click("#order-another")