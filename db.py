import mysql.connector
import config

db = mysql.connector.connect(
    host=config.host,
    user=config.user,
    port=config.port,
    passwd=config.passwd,
    database=config.database,
)

cursor = db.cursor(buffered=True)

# cursor.execute("CREATE DATABASE starshares")

# cursor.execute("CREATE TABLE your_keys (keySubject VARCHAR(42), amount INT(255), buyPrice FLOAT(53), sellPrice FLOAT(53), relativeProfit FLOAT(53), totalSupply INT(255), timeStamp FLOAT(53))")


def show_db() -> None:
    cursor.execute("SELECT * FROM your_keys")
    print(f"Database:")
    for x in cursor:
        print(x)


def update_sellPrice_relativeProfit(
    keySubject, sellPrice, relativeProfit, totalSupply
) -> None:
    cursor.execute(
        "UPDATE your_keys SET sellPrice = %s, relativeProfit = %s, totalSupply = %s WHERE keySubject = %s",
        (
            sellPrice,
            relativeProfit,
            totalSupply,
            keySubject,
        ),
    )
    db.commit()
    # show_db()


def get_database() -> list:
    cursor.execute("SELECT * FROM your_keys")
    your_keys = cursor.fetchall()
    return your_keys


def addKey(keySubject, amount, buyPrice, sellPrice, relativeProfit, timeStamp) -> None:
    cursor.execute(
        "INSERT INTO your_keys (keySubject, amount, buyPrice, sellPrice, relativeProfit, timeStamp) VALUES (%s, %s, %s, %s, %s, %s)",
        (keySubject, amount, buyPrice, sellPrice, relativeProfit, timeStamp),
    )
    db.commit()
    print(
        f"\nKey added:\nSubject: {keySubject}\nAmount: {amount}\nPrice: {buyPrice}\nTimestamp: {timeStamp}\n"
    )
    # show_db()


def rem_key(key_subject):
    cursor.execute("DELETE FROM your_keys WHERE keySubject = %s", (key_subject,))
    db.commit()
    print(f"\nKey deleted: {key_subject}")
    # show_db()

"""
def addError(keySubject, amount):
    cursor.execute(
        "INSERT INTO error_keys (keySubject, amount) VALUES (%s, %s)",
        (keySubject, amount),
    )
    db.commit()
"""