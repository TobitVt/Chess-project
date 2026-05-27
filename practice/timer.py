import threading
import time

def run_input_timer(prompt, remaining_seconds, valid_questions):
    # Check if this specific timer is already empty
    if remaining_seconds <= 0:
        print(f"\r00:00 | {prompt}: ", end="", flush=True)
        return input(), 0, 0

    stop_timer = False

    def countdown():
        nonlocal remaining_seconds, stop_timer
        while remaining_seconds > 0 and not stop_timer:
            mins, secs = divmod(remaining_seconds, 60)
            timer = '{:02d}:{:02d}'.format(mins, secs)
            
            print(f"\r[{timer}] {prompt}: ", end="", flush=True)
            
            time.sleep(1)
            remaining_seconds -= 1
            
        if remaining_seconds == 0 and not stop_timer:
            print(f"\n00:00 - Time's up for this turn!")

    # Start the specific timer thread
    timer_thread = threading.Thread(target=countdown)
    timer_thread.daemon = True
    
    # Track the exact start time
    start_time = time.time()
    timer_thread.start()

    # --- Phase 1: Get Valid Question Choice ---
    chosen_q = ""
    while not stop_timer:
        chosen_q = input().strip().lower()
        if remaining_seconds <= 0:
            break
        if chosen_q in valid_questions:
            print(f"-> Selected: {chosen_q.upper()}")
            break
        print(f"\nInvalid choice! Choose from {list(valid_questions.keys())}: ", end="")

    # --- Phase 2: Get Valid Answer ---
    user_response = ""
    if remaining_seconds > 0 and chosen_q in valid_questions:
        expected_type = valid_questions[chosen_q]["type"]
        print(f"Provide your answer ({expected_type}): ", end="")
        
        while not stop_timer:
            user_response = input().strip()
            if remaining_seconds <= 0:
                break
                
            # Validation rule: Colours must be letters only, foods must not be empty
            if expected_type == "letters only" and not user_response.isalpha():
                print("\nInvalid! Answer must contain letters only: ", end="")
            elif user_response == "":
                print("\nInvalid! Answer cannot be empty: ", end="")
            else:
                break

    # Freeze the timer immediately and track end time
    stop_timer = True
    end_time = time.time()
    
    # Calculate how many full seconds elapsed during this turn
    seconds_taken = round(end_time - start_time)
    
    time.sleep(0.1) 
    print(f"\nTimer frozen! It took you {seconds_taken} seconds.\n")
    
    return chosen_q, user_response, remaining_seconds, seconds_taken

# --- Main Program Flow ---

# 1. Setup global configurations
col_time = int(input("How many seconds total for Colour pool?: "))
foo_time = int(input("How many seconds total for Food pool?: "))

# Tracking data structures
timers = {"colour": col_time, "food": foo_time}
players = ["Player 1", "Player 2"]
history = {"Player 1": [], "Player 2": []}

# Questions bank with structural validation rules
questions_bank = {
    "colour": {"prompt": "What is your favourite colour?", "type": "letters only"},
    "food":   {"prompt": "What is your favourite food?",   "type": "text"}
}

# 2. Game Loop: 2 Rounds for both players
for round_num in range(1, 3):
    print(f"\n================= ROUND {round_num} =================")
    
    for player in players:
        print(f"\n>>> {player}'s Turn <<<")
        print(f"Available Time pools -> Colour: {timers['colour']}s | Food: {timers['food']}s")
        
        # Build dynamic prompt showing available categories
        menu_prompt = f"{player}, type 'colour' or 'food' to pick a question"
        
        # Execute question select + validation + answering within one continuous countdown
        q_choice, user_ans, updated_time, elapsed = run_input_timer(
            menu_prompt, 
            timers["colour"] if timers["colour"] > timers["food"] else timers["food"], # Uses higher pool as execution ceiling
            questions_bank
        )
        
        # Deduct the time spent from the actual chosen question category pool
        if q_choice in timers:
            timers[q_choice] = max(0, timers[q_choice] - elapsed)
            
            # Record historical tracking metrics
            history[player].append({
                "round": round_num,
                "category": q_choice,
                "answer": user_ans if user_ans else "TIMEOUT",
                "time_taken": elapsed,
                "remaining_pool": timers[q_choice]
            })
        
        # Immediate game-over verification check
        if timers["colour"] <= 0 and timers["food"] <= 0:
            print("\nGame Over! All time pools are completely depleted.")
            break
            
    if timers["colour"] <= 0 and timers["food"] <= 0:
        break

# 3. Final Summary Dashboard
print("\n" + "="*15 + " FINAL RESULTS & STATS " + "="*15)
for player in players:
    print(f"\n[{player} Summary]")
    for record in history[player]:
        print(f"  Round {record['round']} | Category: {record['category'].upper()}")
        print(f"    Answer: {record['answer']} | Time Spent: {record['time_taken']}s | Pool Left: {record['remaining_pool']}s")
