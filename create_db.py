import sqlite3

# Connect to SQLite
conn = sqlite3.connect('patients.db')
cursor = conn.cursor()

# Drop if already exists (for re-run)
cursor.execute("DROP TABLE IF EXISTS consultations")

# Create the table
cursor.execute('''
    CREATE TABLE consultations (
        sno INTEGER PRIMARY KEY,
        patient_id TEXT,
        patient_name TEXT,
        consultation_date TEXT,
        consultation_notes TEXT
    )
''')

# Insert realistic and clean patient data
data = [
    # Patient 1
    (1, 'P1', 'Patient 1', '2025-01-14', 'Initial appointment. Reported fever and headache.'),
    (2, 'P1', 'Patient 1', '2025-01-28', 'Reviewed blood test report. No follow-up treatment required.'),

    # Patient 2
    (3, 'P2', 'Patient 2', '2025-02-05', 'Visited with symptoms of cold and cough.'),
    (4, 'P2', 'Patient 2', '2025-02-15', 'Blood test conducted.'),
    (5, 'P2', 'Patient 2', '2025-02-25', 'Diagnosed with typhoid. Vaccine scheduled for 2025-03-04.'),
    (6, 'P3',"Ramesh", "2025-06-10", "Complained of body pain and nausea."),
    (7, 'P3',"Ramesh", "2025-06-17", "Blood test done. Diagnosed with dengue."),
    (8, 'P3',"Ramesh", "2025-06-20", "Prescribed medication. Follow-up suggested after 1 week.")
]

cursor.executemany('INSERT INTO consultations VALUES (?, ?, ?, ?, ?)', data)

conn.commit()
conn.close()

print("✅ Patient database created successfully.")
