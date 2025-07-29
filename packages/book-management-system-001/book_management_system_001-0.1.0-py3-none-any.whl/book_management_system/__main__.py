def run_library_system():
#books
 books = {
    "To Kill a Mockingbird",
    "1984",
    "Pride and Prejudice",
    "The Great Gatsby",
    "The Catcher in the Rye",
    "Moby Dick",
    "Jane Eyre",
    "The Lord of the Rings",
    "Harry Potter and the Sorcerer's Stone",
    "The Hobbit",
    "The Alchemist",
    "The Da Vinci Code",
    "Animal Farm",
    "Brave New World",
    "The Book Thief",
    "The Kite Runner",
    "Sapiens: A Brief History of Humankind",
    "The Diary of a Young Girl",
    "Little Women",
    "The Fault in Our Stars"
}
#users
 user1={
    "The Lord of the Rings",
    "Harry Potter and the Sorcerer's Stone",
    "The Hobbit",
    "The Alchemist"
}
 user2={
    "The Hobbit",
    "The Alchemist",
    "The Da Vinci Code",
    "Animal Farm",
    "Brave New World"
}
 user3={
    "1984"
}

#choice
 print("\n1.Backup of books")
 print("\n2.Add a new book")
 print("\n3.Remove a existing book")
 print("\n4.View available books")
 print("\n5.Issue a book to user")
 print("\n6.Return book from user")
 print("\n7.View issued books")
 print("\n8.All books")
 print("\n9.Comparing issued books between users")
 print("\n10.Checking subset with Issued books")
 print("\n11.Checking superset with issued books")
 print("\n12.Checking disjoint")
 print("\n13.Clear all books")
 print("\n14.Exit")

#copy of the books
 available_books=books.copy()

 while True:
 #Getting choice from user
  choice=int(input("\nEnter the choice [1-14] :"))


 #backup of books
  if choice == 1:
   book_copy=books.copy()
   print("\nCopy of the books:",book_copy)

 #add new books
  elif choice == 2:
   new_book_name=input("\nEnter the book name to add: ")
   if new_book_name not in book_copy:
    books.add(new_book_name)
    available_books.add(new_book_name)
    print("\nSuccessfully added")
   else:
    print("\nAlready book in the library")
 
 #Remove a already existing book
  elif choice == 3:
   remove_book_name=input("\nEnter the book name to remove: ")
   if remove_book_name not in books.copy():
    print("\nThe book is not in library")   
   else:
    books.remove(remove_book_name)
    print("\nThe book is removed in library")
 
 #viewing available books
  elif choice == 4:
  #available_books=books
   print("\nAvailable books:",available_books)

 #Issue book to user
  elif choice == 5:
  #print("\nThe book is available or not?")
   wanted_book=input("\nEnter the wanted book: ") 
   user=input("\nEnter the which user: ")
   if wanted_book in available_books:
    print("\nBook is Available")
    if user == "user1":
     available_books.remove(wanted_book)
     user1.add(wanted_book)
     print("User1 :",user1)
    elif user == "user2":
     available_books.remove(wanted_book)
     user2.add(wanted_book)
     print("User2 :",user2)
    else:
     available_books.remove(wanted_book)
     user3.add(wanted_book)
     print("User3 ",user3)
   else:
    print("\nBook is not available")

 #return book
  elif choice == 6:
  #print("\nThe book is available or not?")
   return_book=input("\nEnter the Return book: ") 
   user=input("\nEnter the which user: ")
   if return_book in user1 or user2 or user3:
    print("\nReturning..")
   if user == "user1":
    available_books.add(return_book)
    books.update(return_book)
    user1.remove(return_book)
    print("User1 :",user1)
   elif user == "user2":
    available_books.add(return_book)
    books.update(return_book)
    user2.remove(return_book)
    print("User2 :",user2)
   elif user == "user3":
    available_books.add(return_book)
    books.update(return_book)
    user3.remove(return_book)
    print("User3 :",user3)
   else:
    print("\nInvaild user")
  
   print("\nBook is not available")
 
 #View Issued Books
  elif choice == 7:
   issued_books=user1|user2|user3
   print("\nIssued Books: ",issued_books)

 #View all books
  elif choice == 8:
   print("\nAll Books: ",books)

 #Comparing Issued Books Between Users
  elif choice == 9:
  #common books between users
   common_books=user1 & user2 & user3
   print("\nCommon books: ",common_books)

  #unique books
   unique_books=user1-user2-user3
   print("\nUnique books: ",unique_books)

 #subset 
  elif choice == 10:
   if user1 <= books:
    print("\nIt is a subset of all books")
   else:
    print("\nIt is not a subset of all books") 
 
 #superset
  elif choice == 11:
   if user2 >= books:
    print("\nIt is a superset for issued books")
   else:
    print("\nIt is not a superset for issued books")

 #disjoint
  elif choice == 12:
   if user1.isdisjoint(user2) == True:
    print("\nIt is disjoint")
   else:
    print("\nIt is not disjoint")

 #clear
  elif choice == 13:
   books.clear()
   print("\nAfter clear the books are :",books)

 #exit
  elif choice == 14:
   print("\nExisting..")
   break

 #Invalid choice
  else:
   print("\nInvaild choice")
   break
 
 if __name__ == "__main__":
    run_library_system()
