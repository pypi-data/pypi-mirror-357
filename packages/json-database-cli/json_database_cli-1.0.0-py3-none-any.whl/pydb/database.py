import os
import json
import argparse
import sys

def format_file(name: str) -> str:
    return name if name.endswith(".json") else f"{name}.json"

def parse_kv_pairs(pairs):
    try:
        return {k: v for k, v in (p.split("=", 1) for p in pairs)}
    except ValueError:
        print("Each field must be in key=value format.")
        sys.exit(1)

class Database:
    def __init__(self, filename: str):
        self.name = filename
        self.data = {}

        if os.path.exists(self.name) and os.path.getsize(self.name) > 0:
            try:
                with open(self.name, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                print(f"Database '{self.name}' loaded.")
            except json.JSONDecodeError:
                print(f"Warning: '{self.name}' is not valid JSON — starting with an empty DB.")
        else:
            with open(self.name, "w", encoding="utf-8") as f:
                json.dump({}, f)
            print(f"New database '{self.name}' created.")

        self.next_id = max(map(int, self.data.keys()), default=0) + 1

    def _save(self):
        with open(self.name, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4)

    def add(self, record: dict):
        self.data[str(self.next_id)] = record
        self.next_id += 1
        self._save()
        print("Record added.")

    def read(self, id: str | None = None):
        if id is None or id == "":
            print(json.dumps(self.data, indent=4))
        else:
            id = str(id)
            if id in self.data:
                print(json.dumps(self.data[id], indent=4))
            else:
                print(f"ID {id} not found.")

    def update(self, id: str, new_record: dict):
        id = str(id)
        if id in self.data:
            self.data[id] = new_record
            self._save()
            print("Record updated.")
        else:
            print(f"ID {id} not found.")

    def alter(self, id: str, key: str, value: str, strict: bool = False):
        id = str(id)
        if id not in self.data:
            print(f"ID {id} not found.")
            return
        if strict and key not in self.data[id]:
            print(f"Key '{key}' not present in record {id}.")
            return
        self.data[id][key] = value
        self._save()
        print("Field updated.")

    def delete(self, id: str):
        id = str(id)
        if id in self.data:
            del self.data[id]
            self._save()
            print(f"Record {id} deleted.")
        else:
            print(f"ID {id} not found.")

    def search(self, key, target):
        for id, record in self.data.items():
            if record.get(key) == target:
                return id                
        print("Item not found")          
        return None


    def find(self , condtions):
        for id , record in self.data.items():
            match = True        
            for k , v in condtions.items():
                if str(record.get(k)) != str(v):
                    match = False
                    break
            if match:
                print(f'ID {id}: ' , record)


    def import_csv(self , filename):
        import csv
        try:
            with open(filename , 'r' , encoding='utf=8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    self.add(row)
                    count += 1
                print(f"Imported {count} records from {filename}")
        except FileNotFoundError:
            print(f"File '{filename}' not found")
        except Exception as e:
            print(f"Error importing CSV: {e}")                

def main():
    parser = argparse.ArgumentParser(description="Simple JSON database CLI")

    parser.add_argument("-d", "--db", required=True, help="Database name (without .json extension)")
    parser.add_argument("--add", nargs="+", metavar="key=value", help="Add a record")
    parser.add_argument("--read", nargs="?", const="", metavar="ID", help="Read record (omit ID to read all)")
    parser.add_argument("--update", nargs="+", metavar=("ID", "key=value"), help="Replace entire record by ID")
    parser.add_argument("--alter", nargs=3, metavar=("ID", "KEY", "VALUE"), help="Alter single field in a record")
    parser.add_argument("--delete", metavar="ID", help="Delete record by ID")
    parser.add_argument("--search", nargs=1, help="Seach a target and return its Id.")
    parser.add_argument("--find" , nargs='+', metavar=("key=value") , help="Find a record based on given condition" )
    parser.add_argument("--import_csv", metavar=("Filename"), help="Import csv file and convert into JSON")



    args = parser.parse_args()

    db_file = format_file(args.db)

    if not os.path.exists(db_file):
        with open(db_file, "w", encoding="utf-8") as f:
            json.dump({}, f)

    db = Database(db_file)

    if args.add:
        db.add(parse_kv_pairs(args.add))

    elif args.read is not None:
        db.read(args.read)

    elif args.update:
        if len(args.update) < 2:
            print("Usage: --update ID key=value [key=value ...]")
        else:
            rec_id = args.update[0]
            kv_pairs = parse_kv_pairs(args.update[1:])
            db.update(rec_id, kv_pairs)

    elif args.alter:
        rec_id, key, value = args.alter
        db.alter(rec_id, key, value)

    elif args.delete:
        db.delete(args.delete)
        
    elif args.search:
        try:
            key, value = args.search[0].split("=", 1)
            result = db.search(key, value)
            if result:
                print(f"Found at ID {result}")
            else:
                print("No match found.")
        except ValueError:
            print("Search must be in key=value format.")

    elif args.find:
        conditions = parse_kv_pairs(args.find)
        db.find(conditions)

    elif args.import_csv:
        db.import_csv(args.import_csv)   
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
