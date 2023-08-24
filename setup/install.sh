#!/bin/bash

current_dir="$(dirname "$0")"
cd "$current_dir/.."

while true; do
    clear
    echo "Installation menu"
    echo "================="
    echo ""
    echo "[1] Install requirements"
    echo "[2] Start app"
    echo "[3] Exit"
    echo ""
    read -p "Please select: " choose

    case $choose in
        1)
            clear
            echo "Install requirements."
            python3 -m venv venv
            source venv/bin/activate
            python3 -m pip install --upgrade pip
            pip install -r requirements.txt
            deactivate

            echo "Finished."

            while true; do
                read -p "Do you want to start the app now? [y/n]: " choice
                case $choice in
                    y)
                        cd start
                        osascript run.scpt
                        exit 0
                        ;;
                    n)
                        break
                        ;;
                    *)
                        echo "Invalid choice. Please enter 'y' or 'n'."
                        ;;
                esac
            done
            ;;

        2)
            if [ ! -d "venv" ]; then
                clear
                echo "Please install the requirements first."
                echo "Press any key to continue."
                read -n 1 -s
            else
                cd start
                osascript run.scpt
                exit 0
            fi
            ;;

        3)
            exit 0
            ;;

        *)
            ;;
    esac
done
