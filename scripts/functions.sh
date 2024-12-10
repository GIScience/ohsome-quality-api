# donation by mcauer as used in the 'ohsome-dashboard' project

prompt_user() {
    local question="$1"  # Capture the first argument as the question
    while true; do
        read -p "$question (y/n): " choice
        case "$choice" in
            y|Y )
                echo "You chose Yes."
                return 0  # Exit the function and proceed
                ;;
            n|N )
                echo "You chose No. Exiting."
                exit 0  # Exit the script
                ;;
            * )
                echo "Invalid input. Please enter 'y' or 'n'."
                ;;
        esac
    done
}


run_sed() {
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  sed --in-place=.bak "$1" "$2"
elif [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i .bak "$1" "$2"
else
  printf "\nOS could not be detected. Please open report manually!\n"
fi
}

# Example usage
#prompt_user "Do you want to continue?"

# import in other script

## Get the directory of the current script
 #SCRIPT_DIR="$(dirname "$0")"
 #
 ## import user prompt
 #source "$SCRIPT_DIR/functions.sh"
