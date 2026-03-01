# Pending Task List Program

pending_tasks = []

print("Welcome to Your Task Manager!")

while True:
    task = input("Enter a task to add to your pending list: ")
    
    pending_tasks.append(task)
    print("Task added successfully!")

    choice = input("Do you want to add more tasks? (yes/no): ").lower()
    
    if choice == "no":
        break

print("\nYour Pending Tasks:")
for i, task in enumerate(pending_tasks, start=1):
    print(f"{i}. {task}")

print("Thank you! Exiting Task Manager.")