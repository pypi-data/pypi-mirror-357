# Conditional assignments with complex conditions
ifeq ($(origin CC),undefined)
    CC = gcc
    $(info DEBUG: CC was undefined, set to gcc) # Info message for debugging
else
    $(info DEBUG: CC was defined as "$(CC)" (origin: $(origin CC)))
endif

ifneq (,$(findstring gcc,$(CC)))
    COMPILER_FLAGS = -Wall -Wextra
    $(info DEBUG: CC contains "gcc", COMPILER_FLAGS set to "$(COMPILER_FLAGS)")
else
    COMPILER_FLAGS = # Ensure it's empty if gcc is not found
    $(info DEBUG: CC does not contain "gcc", COMPILER_FLAGS remains empty or default)
endif

# Target to display variables
test_vars:
	@echo "--- Testing Makefile Variables ---"
	@echo "Value of CC: $(CC)"
	@echo "Value of COMPILER_FLAGS: $(COMPILER_FLAGS)"
	@echo "Origin of CC: $(origin CC)"
	@echo "----------------------------------"

# Clean target (good practice)
clean:
	@echo "Cleaning up..."
	@rm -f *.o my_program # Example clean commands, adjust as needed
