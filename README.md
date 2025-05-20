# Car Registration Records Management Application

This is a Python desktop application for managing the registration records of vehicles. It was developed as part of the Programming Algorithm's Laboratory course at the Faculty of Automation, Computers and Electronics, University of Craiova (http://ace.ucv.ro/).

## Features

- Vehicle Registration  
  Add new cars by filling out a user-friendly form.

- Display of Registered Vehicles  
  View a searchable and sortable table of all vehicles in the database.

- Live Search and Sorting  
  Search for entries and sort the table by clicking on the column headers.

- In-place Editing  
  Double-click on any table cell to edit and automatically update the database.

- Record Deletion  
  Delete any vehicle entry directly from the interface.

- OCR-Based Auto-Fill  
  Upload a photo of the vehicle registration certificate using your phone (via QR code) and automatically fill in the form using OCR.

- Position-based OCR Mapping  
  Data is extracted based on the relative position of fields in Romanian car registration certificates, improving flexibility over strict label recognition.

- Real-time OCR Integration  
  After image upload, the data is auto-filled into the form fields for review and confirmation.

## Known Issues / Limitations

- OCR may struggle with poor lighting or blurry images.
- Certificate layout variations between counties may occasionally reduce accuracy.
- No user authentication or access control has been implemented.
- The UI is optimized for desktop and may not display properly on very small screens.

## Technologies Used

- Python 3
- Tkinter
- SQLite
- OpenCV
- pytesseract
- Flask (for QR-based image upload)
