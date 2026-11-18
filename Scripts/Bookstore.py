from Queue import Queue
from Stack import Stack
import random

def main():
    print()
    print("CITA 225 Bookstore Inventory System")
    print("Enter the number that corresponds to your selection.")
    menu()

def menu():
    # This menu function contains all of the logic of our "program."
    # As the user selects options, various related functions are called. 

    inventory = []  # This empty list will contain "books" of type dictionary and 
                    # will represent our inventory. 
    salesStack = Stack()  # This empty stack will store purchases as they are made.
                          # They will be popped when we generate a sales report. 
    salesReport = []  # This list will contain dictionary entries for every sale
                      # in reverse-chronological order (most recent first).

    # Create starting inventory and sales stack
    initializeTestData(inventory, salesStack)

    while True:
        print()
        print("   MAIN MENU\n"
                    "1: Add Book\n"
                    "2: Place Order\n"
                    "3: Restock Book\n"
                    "4: Show Sales Report\n"
                    "5: Show Inventory\n"
                    "6: Show Waitlists\n"
                    "7: Show Unique Authors\n"
                    "8: Quit\n")
        num = int(input("Pick an Option: "))

        if num == 1:
            addBook(inventory)
        elif num == 2:
            placeOrder(inventory, salesStack)
        elif num == 3:
            restock(inventory, salesStack)
        elif num == 4:
            showSales(salesStack, salesReport)
        elif num == 5:
            showInventory(inventory)
        elif num == 6:
            showWaitlists(inventory)
        elif num == 7:
            showAuthors(inventory)
        elif num == 8:
            endProgram()
        else:
            print("Invaild input")

# This function is called in Option 1: Add Book
def addBook(inventory: list):
    # This function adds book to our inventory in the form of a
    # dictionary that has all the info about that book.
    
    print()

    # Create a new book with user entered info
    newBook = dict(
        Title = input("Enter the title: "), 
        Author = input("Enter the author: "), 
        ISBN = int(input("Enter the ISBN: ")), 
        Stock = int(input("Enter the stock: ")),
        Price = float(input("Enter the Price: ")),
        Waitlist = Queue() # Create an empty queue that will
                           # act as the waitlist for this book.
    )

    print()

    # Compare the title and ISBN of the new book to all the books already
    # in our inventory to prevent duplicates from being added.
    if any(book["ISBN"] == newBook["ISBN"] for book in inventory) \
    or any(book["Title"].lower() == newBook["Title"].lower() for book in inventory):
        print(f"A book with title {newBook['Title']} or ISBN {newBook['ISBN']} " +
                "already exists in our inventory")
    else: # If no duplicates are found, append our inventory list with the new book.
        inventory.append(newBook)
        print(f"{newBook['Stock']} copies of the book {newBook['Title']} " +
            f"by {newBook['Author']} have been added to your inventory.")
    
    # Sort for readability
    sortInventory(inventory)


# This function is called in Option 2: Place Order
def placeOrder(inventory: list, salesStack: Stack):
    # This function asks for the customer's name, the title of the book they
    # want to order, and the number they want to order. It then places the order,
    # adds them to a waitlist, or both, depending on how many they want. 
    
    print()

    # Get user input
    custName = input("Enter your name: ")
    title = input("Enter the title: ")
    orderQuantity = int(input("Enter the purchase amount: "))

    # If the book they want has exactly 0 stock, add to waitlist
    if checkStockByTitle(inventory, title) == 0:
        for book in inventory:
                if book["Title"].lower() == title.lower():
                    addToWaitlist(book["Waitlist"], custName, title, orderQuantity)
    # If the book has stock > 0, fill their order and add them to the waitlist if
    # they ordered more than we have in stock.
    elif checkStockByTitle(inventory, title) != None:
        stock = checkStockByTitle(inventory, title)
        # If we have more than they want, we fill the sale as normal and
        # reduce the stock by the amount they bought. 
        if stock >= orderQuantity:
            for book in inventory:
                if book["Title"].lower() == title.lower():
                    book["Stock"] -= orderQuantity
                    totalPrice = orderQuantity * book["Price"]
                    recordSale(salesStack, custName, book["Title"], book["Author"], 
                               book["ISBN"], orderQuantity, totalPrice)
        # If they want more than we have, we sell them every copy we have, then add
        # them to the waitlist for the remaining copies they still want. 
        else:
            for book in inventory:
                if book["Title"].lower() == title.lower():
                    overOrder = orderQuantity - stock
                    orderQuantity = stock
                    book["Stock"] = 0
                    totalPrice = orderQuantity * book["Price"]
                    recordSale(salesStack, custName, book["Title"], book["Author"], book["ISBN"], orderQuantity, totalPrice)
                    addToWaitlist(book["Waitlist"], custName, book["Title"], overOrder)
    # If checking the title returns None, it means that the book doesn't exist in our inventory.
    else:
        print(f"{title} is not in our inventory.")


def addToWaitlist(waitlist: dict, custName: str, title: str, quantity: int):
    # This function creates a dictionary containing a customer name, book title, and quantity
    # and adds it to the waitlist for that book. 
    waitlist.enqueue(dict(Customer = custName, Title = title, Quantity = quantity))
    print()
    print(f"{custName}'s request for {quantity} copies of {title} have been " +
          "added to the waitlist.")


# This function is called in Option 3: Restock
def restock(inventory: list, salesStack: Stack):
    # This function asks the user for book restock info. It then fulfills any
    # waitlist orders, then restocks the inventory with remaining restock amount.
    title = input("Enter the title: ")
    restockAmount = int(input("Enter the stock to add: "))

    # If the book is in our inventory, even if stock is 0
    if checkStockByTitle != 0:
        for book in inventory:
            if book["Title"].lower() == title.lower():
                # This while loop will run as long as we still have an amount
                # we're restocking AND there is still customers in the waitlist
                while restockAmount > 0 and not book["Waitlist"].isEmpty():
                    nextOrder = book["Waitlist"].peek()
                    orderQuantity = nextOrder["Quantity"]

                    # If we're restocking more than the first waitlist customer
                    # wants, we fill their order. 
                    if orderQuantity <= restockAmount:
                        recordSale(salesStack, nextOrder["Customer"], book["Title"], book["Author"],
                                book["ISBN"], orderQuantity, orderQuantity * book["Price"])
                        book["Waitlist"].dequeue()
                        restockAmount -= orderQuantity
                    # If they want more than we are restocking, we need to dequeue the waitlist
                    # into a temp list to edit the first entry. We then fill as much of their 
                    # request as we can, then requeue the waitlist with the adjusted order. 
                    else:
                        tempOrders = [] 
                        while not book["Waitlist"].isEmpty():
                            tempOrders.append(book["Waitlist"].dequeue())
                        
                        orderFilled = restockAmount
                        tempOrders[0]["Quantity"] -= restockAmount

                        recordSale(salesStack, tempOrders[0]["Customer"],
                                book["Title"], book["Author"], book["ISBN"],
                                orderFilled, orderFilled * book["Price"])
                        restockAmount = 0

                        for order in tempOrders:
                            book["Waitlist"].enqueue(order)
                        tempOrders.clear()

                # Finally we restock with any leftovers after handling waitlists
                # If there wasn't any waitlists, this restockAmount will be the 
                # original amount entered by the user. 
                book["Stock"] += restockAmount
    # The book isn't in our inventory
    else:
        print(f"{title} is not in our inventory.")


# This function is called in Option 4: Show Sales Report
def showSales(salesStack: Stack, salesReport: list):
    # This function pops our salesStack into a temporary list, then 
    # prepends (adds to beginning) that list to our overall salesReport
    # list. Finally, it prints a formatted table with the results.
    tempSales = []
    while not salesStack.isEmpty():
        tempSales.append(salesStack.pop())
    
    salesReport[:0] = tempSales

    # Formatted Table
    print()
    print(f"    Sales Report    ")
    print(f" Customer |  Title  |    Author   | ISBN | Quantity | Total Price")
    print("------------------------------------------------------------")
    for sale in salesReport:
        print(f"{sale["Customer"]:<10}| {sale["Title"]:^8}| {sale["Author"]:<12}| " +
              f"{sale["ISBN"]:^4} | {sale["Quantity"]:^8} |  ${sale["TotalPrice"]:>9.2f}")


# This function is called in Option 5: Show Inventory
def showInventory(inventory: list):
    # This function prints a formatted table contained each book in our inventory
    print()
    print(f"{"Bookstore Inventory":^25}")
    print(f"{"TITLE":^9}|{"Author":^14}|{"ISBN":^6}|{"STOCK":^7}|{"PRICE":^10}|{"WAITLIST":^10}")
    print("------------------------------------------------------------")
    for book in inventory:
        print(f"{book["Title"]:^9}|  {book["Author"]:<12}|{book["ISBN"]:^6}|" +
              f"{book["Stock"]:^7}|  ${book["Price"]:>7.2f}|{book["Waitlist"].getSize():^10}")


# This function is called in Option 6: Show Waitlists
def showWaitlists(inventory: list):
    # This function prints a formatted table for each book with stock of 0
    # and with people on the waitlist. Because we can't iterate through a Queue,
    # we have to use the same trick we used while handling restocking: we dequeue
    # into a list first, print the table, then requeue exactly as is. 
    tempWaitlist = []
    for book in inventory:
        if book["Waitlist"].getSize() != 0:
            print()
            print(f"        {book["Title"]} Waitlist        ")
            print("    Name    |    Title   |   Quantity")
            print("----------------------------------------")
            while not book["Waitlist"].isEmpty():
                tempWaitlist.append(book["Waitlist"].dequeue())

            for entry in tempWaitlist:
                print(f"{entry["Customer"]:^11} | {entry["Title"]:^10} | " +
                      f"{entry["Quantity"]:^12}")
                book["Waitlist"].enqueue(entry)
            tempWaitlist.clear()
            

# This function is called in Option 7: 
def showAuthors(inventory: list):
    # This function iterates through each book in our inventory and
    # adds the unique (non-repeating) authors to a list, and prints the result. 
    authors = []
    for book in inventory:
        if book["Author"] not in authors:
            authors.append(book["Author"])
    authors.sort()
    print("Unique Authors: ", end="")
    for author in authors:
        print(author, end=", ")
    print()


# This function is called in Option 8: Quit
def endProgram():
    # This function ends the program.
    print()
    print("The program will now end.")
    print()
    quit()


def sortInventory(inventory: list):
    # This function sorts the inventory by title and returns the result.
    return inventory.sort(key=getTitle)


# This function is used in sortInventory() to define what
# parameter we want to sort our inventory by. Default is title
def getTitle(book: dict):
    return book["Title"]


def checkStockByTitle(inventory: list, title: str):
    # This function checks a given title against our inventory. 
    # If the book is in our inventory, it returns that book's stock.
    for book in inventory:
        if book["Title"].lower() == title.lower():
            return book["Stock"]
    return None
    

# This function is called within placeOrder() and restock() when we are filling customer orders
def recordSale(salesStack: Stack, custName: str, title: str, author: str, 
               isbn: int, orderQuantity: int, totalPrice: float):
    # This function takes given data about a sale and pushes a 
    # dictionary containing that data to our salesStack.
    salesStack.push(dict(
        Customer = custName,
        Title = title,
        Author = author,
        ISBN = isbn,
        Quantity = orderQuantity,
        TotalPrice = totalPrice
    ))

    print()
    print(f"{custName} bought {orderQuantity} copies of {title} " +
        f"for a total price of ${totalPrice:.2f}")


# This function is called at the beginning of our program to 
# create data that we can use for testing. 
def initializeTestData(inventory: list, salesStack: Stack):
    authors = ["Max V", "Gabbie P", "Mustafa E", 
               "Khalfalla A", "Stephen K", "Patrick C",
               "James V"]
    
    # Create 10 test books
    for i in range(1, 11):
        inventory.append({
            "Title": f"CITA{200+i}",
            "Author": random.choice(authors),
            "ISBN": 1000 + i,
            "Stock": random.randint(0, 10),
            "Price": round(random.uniform(10, 50), 2),
            "Waitlist": Queue()
        })
    
    # Create 12 test sales
    customers = ["Alice", "Bob", "Charlie", "Dana", "Eve", 
                 "Frank", "Grace", "Heidi", "Ivan", "Judy"]
    for i in range(12):
        book = random.choice(inventory)
        qty = random.randint(1, 3)
        salesStack.push(dict(
            Customer = random.choice(customers),
            Title = book["Title"],
            Author = book["Author"],
            ISBN = book["ISBN"],
            Quantity = qty,
            TotalPrice = round(qty * book["Price"], 2)
        ))  

if __name__ == "__main__":
    main()
