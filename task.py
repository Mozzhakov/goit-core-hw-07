from collections import UserDict
from datetime import datetime

################################################ Classes

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
         if not value or len(value) < 2:
             raise ValueError('Name is required and must contain more than 2 symbols')
         super().__init__(value)
    
class Phone(Field):
    def __init__(self, value):
         if not value.isdigit() or len(value) != 10:
              raise ValueError('Phone number should contain 10 digits')
         super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_object = datetime.strptime(value, "%d.%m.%Y")  
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        if birthday_object > datetime.today():
            raise ValueError("Birthday can't be in future")
        super().__init__(birthday_object.date()) 

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, date):
        self.birthday = Birthday(date)

    def add_phone(self, number):
        self.phones.append(Phone(number))

    def delete_phone(self, number):
        self.phones = [phone for phone in self.phones if phone.value != number]

    def find_phone(self, number):
        for phone in self.phones:
            if number == phone.value:
                return phone
        return None
    
    def edit_phone(self, old_number, new_number):
        phone = self.find_phone(old_number)
        if phone:
            try:
                new_phone = Phone(new_number)
            except ValueError as e: 
                raise ValueError(f'Invalid phone number: {e}')
            self.delete_phone(old_number)
            self.phones.append(new_phone)
        else:
            raise ValueError('Phone number not found')
    
    def __str__(self):
        birthday_str = self.birthday.value if self.birthday else "No birthday"
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {birthday_str}"


################################################ AddressBook

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError('Contact not found')
    
    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []
        days = 7
        for record in self.data.values():
            if record.birthday:
                birthday = record.birthday.value
                birthday_this_year = birthday.replace(year=today.year)
                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= days:
                    upcoming_birthdays.append({
                        "Name": record.name.value,
                        "birthday date": birthday_this_year.strftime('%d.%m.%Y')
                    })
        return (f"Birthdays in the next {days} days: {upcoming_birthdays}" if len(upcoming_birthdays) > 0 else f"No one has birthday in the next {days} days.")

    
    def __str__(self):
        return f'Your contacts:\n{'\n'.join(str(record) for record in self.data.values())}'

################################################ Handlers

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Contact not found..."
        except IndexError:
            return "Enter a valid command with necessary arguments."
    return inner

################################################ Contact functions

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    name = name.capitalize()
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error    
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args
    name = name.capitalize()
    record = book.find(name)
    message = 'Contact not found'
    if record is not None:
        record.edit_phone(old_phone, new_phone)
        message = "Contact updated"
    return message

@input_error
def delete_number(args, book: AddressBook):
    name, phone, *_ = args
    name = name.capitalize()
    record = book.find(name)
    message = "Contact not found"
    if record is not None and phone is not None:
        record.delete_phone(phone)
        message = "Phone number deleted."
    return message

@input_error
def delete_contact(args, book: AddressBook):
    name, *_ = args
    name = name.capitalize()
    book.delete(name)
    return "Contact deleted."

@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args
    name = name.capitalize()
    record = book.find(name)
    if record is not None:
        return record
    else:
        return 'Contact not found.'
    
################################################ Birthday functions

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args
    name = name.capitalize()
    record = book.find(name)
    message = "Contact not found."
    if record is not None:
        record.add_birthday(birthday)
        message = f'Birthday added to contact {name}'
    return message

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args
    name = name.capitalize()
    record = book.find(name)
    if record is not None:
        return record.birthday
    else:
        return "Contact not found."

@input_error
def birthdays(book: AddressBook):
    return book.get_upcoming_birthdays()

################################################ Main function

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        match command:
            case 'exit' | 'close':
                print("Good bye!")
                break
            case 'hello':
                print("How can I help you?")
            case 'add': 
                print(add_contact(args, book))
            case 'change':
                print(change_contact(args, book))
            case 'delete-number':
                print(delete_number(args, book))
            case 'delete':
                print(delete_contact(args, book))
            case 'phone':
                print(show_phone(args, book))
            case "all":
                print(book)
            case "add-birthday":
                print(add_birthday(args, book))
            case "show-birthday":
                print(show_birthday(args, book))
            case "birthdays":
                print(birthdays(book))
            case _:
                print("Invalid command.")
    
if __name__ == "__main__":
    main()

