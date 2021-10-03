Assumption 1) 
There is at least 1 alphanumeric character in either the user's first or last name, otherwise a user handle cannot be generated. 
Assumption 2)
A negative start value will not be assessed in the automarking for function channel_messages_v1.
Assumption 3)
For function channel_messages_v1, when you return from each index, 'start' is inclusive however 'start + 50' is exclusive.
Assumption 4)
When we return function clear_v1, we are not expecting to get an empty dictionary otherwise everytime that we call 'clear' we would receive a '{}' in return. 
Assumption 5)
In section 6.2 in the project overview, everytime it has return {} for a function such as for channel_join_v1, {} does not represent a dictionary. 