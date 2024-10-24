import psycopg2

# will be used to read car data from the database
def ReadMethod(cursor):
    try:
        cursor.execute("SELECT * from CARS;")
        print(cursor.fetchall()) # fetchone to fetch only one row (just throwing this in here so i dont forget)
    except Exception as e:
        print(f"Error, stinky read: {e}")

# will write the image bits to the database
def WriteMethod(cursor):
    try:
        # this is a test for now. 
        # cursor.execute("INSERT INTO cars (carid, plate, color) VALUES (%s, %s, %s)", ("cc3363a2-92d9-4f87-85ca-9c8d30b6d53c", "123457", "Navdeep"))
        print("Senjamin Bimonson wrote!")
    except Exception as e:
        print(f"Error, stinky write: {e}")

def main():
    print("Opening secrets")
    f = open("/home/parkings/Desktop/TemporaryConnectionFolder/secrets/db_conn.txt")
    
    # extract data from file. I am lazy so I will just read all of the lines because i know them
    host = str(f.readline()).strip() # this is janky but it works, i am tired and dont want to figure out a better way rn
    port = str(f.readline()).strip()
    dbname = str(f.readline()).strip()
    user = str(f.readline()).strip()
    password = str(f.readline()).strip()

    print("Senjamin Bimonson would like to connect to the database.")
    
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        print("Senjamin Bimonson has connected!")

    except Exception as e:
        print(f"Error, you are stinky: {e}")

    # infinite while loop when done connecting
    # ReadMethod(cursor) # attempt to read
    # WriteMethod(cursor) # stage a write
    # # cursor.close() # will use this to close the connection
    # conn.commit() # commit writes
    #ReadMethod(cursor)

if __name__ == "__main__":
    main()