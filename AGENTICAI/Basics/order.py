# Simple Shopping Cart Program

def shopping_cart():
    print("Welcome to Online Shopping System")
    
    # 1. Ask user details
    name = input("Enter your Name: ")
    email = input("Enter your Email: ")
    phone = input("Enter your Phone Number: ")
    payment_method = input("Enter Payment Method (UPI/Card/Cash): ")
    
    total = 0
    
    # 2. Ask user items and price
    while True:
        item = input("Enter item name to add to cart: ")
        price = float(input("Enter price of the item: "))
        
        total += price
        
        more = input("Do you want to add more items? (yes/no): ").lower()
        if more != "yes":
            break
    
    # 3. Display total price
    print("\n----- BILL DETAILS -----")
    print("Customer Name:", name)
    print("Email:", email)
    print("Phone:", phone)
    print("Payment Method:", payment_method)
    print("Total Amount: ₹", total)
    
    # 4. Order confirmation
    print("\nOrder Confirmed! Thank you for shopping.")
    

# 5. Repeat purchase option
while True:
    shopping_cart()
    again = input("\nDo you want to purchase again? (yes/no): ").lower()
    if again != "yes":
        print("Thank you! Visit again.")
        break