import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich import box
import matplotlib.pyplot as plt

console = Console()

def load_dataset():
    filepath = Prompt.ask("Enter the path to your dataset")
    try:
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith((".xls", ".xlsx")):
            df = pd.read_excel(filepath)
        else:
            console.print("Unsupported file format!", style="bold red")
            return None
        console.print(f"[bold green]Dataset loaded successfully![/bold green]")
        return df
    except Exception as e:
        console.print(f"[bold red]Error loading file:[/bold red] {e}")
        return None

def display_summary(df):
    table = Table(title="Dataset Summary", box=box.MINIMAL)
    table.add_column("Column", justify="left")
    table.add_column("Type", justify="center")
    table.add_column("Non-Null Count", justify="right")
    table.add_column("Unique Values", justify="right")
    
    for col in df.columns:
        table.add_row(
            col, 
            str(df[col].dtype), 
            str(df[col].notnull().sum()), 
            str(df[col].nunique())
        )
    console.print(table)

def filter_data(df):
    column = Prompt.ask("Enter the column to filter by")
    if column not in df.columns:
        console.print(f"[bold red]Column '{column}' not found![/bold red]")
        return df
    condition = Prompt.ask("Enter the condition (e.g., > 50, == 'value')")
    try:
        filtered_df = df.query(f"{column} {condition}")
        console.print(f"[bold green]Filtered {len(filtered_df)} rows![/bold green]")
        return filtered_df
    except Exception as e:
        console.print(f"[bold red]Error filtering data:[/bold red] {e}")
        return df

def main():
    console.print("[bold cyan]Data Science Center![/bold cyan]")
    df = None
    
    while True:
        console.print("\n[bold magenta]Menu:[/bold magenta]")
        console.print("1. Load Dataset")
        console.print("2. Display Summary")
        console.print("3. Filter Data")
        console.print("4. Exit")
        
        choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            df = load_dataset()
        elif choice == "2" and df is not None:
            display_summary(df)
        elif choice == "3" and df is not None:
            df = filter_data(df)
        elif choice == "4":
            console.print("[bold cyan]Goodbye![/bold cyan]")
            break
        else:
            console.print("[bold red]Invalid option![/bold red]")

if __name__ == "__main__":
    main()
 
