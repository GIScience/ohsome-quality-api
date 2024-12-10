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

# Example usage
#prompt_user "Do you want to continue?"

# import in other script

## Get the directory of the current script
 #SCRIPT_DIR="$(dirname "$0")"
 #
 ## import user prompt
 #source "$SCRIPT_DIR/prompt_user_exit_or_continue.sh"