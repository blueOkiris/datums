# Datums

## Description

A data-oriented esoteric programming language with (basically) only 3 commands

## How to program (JUST THE BASIC INSTRUCTIONS)

In datums, you can really do three things

Set data, pause the ability to set data until resume is called a certain amount of times, and do the resume call.

You can also define a data 'type' that takes up a certain amount of space

The commands are:

1) Type definition

   - There are built in types that correspond to typical sizes

   - char -> 1, short -> 2, int -> 4, long -> 8

   - Using this command, you can define your own

   - '#' \<identifier\> \<datasize\>

2) Pause assignments

   - Like I said before, you can 'pause' assignment statements for a certain number of calls to resume. It's kind of like INTERCAL

   - '!' \<address or number\>

   - Example: !(25 : 1) will skip all assignment statements until you've called resume the 'char' pointed to by address 25

   - Note that numbers are numbers, numbers in parenthesis are pointers, so '(' whatever : type')' is like "type \*whatever" in C, and when giving and address, you must say how you want the data represented, which is determined by the type given after the colon

3. Resume

   - By placing one of these, you decrease the counter until you can assign values again

   - Just a single '>'

4. Assignments

   - There are six types of assignments.

   - You have '=,' '+=,' '-=,' '*=,' '/=,' and '%=' which all function as you'd expect in other languages

   - This is best explained by example:

   - `(3 : long) += 00 01 00 01 00 32 00 00 00;`

   - In this example, the data on the right (all in decimal btw), is added to memory location 3, 4, 5, 6, 7, 8, 9, 10, i.e. 3 through 3 + 8 - 1. 8 bytes of data, 1 long, is added into address 3

And that's it

## Hello World Explanation (IMPORTANT FOR UNDERSTANDING)

In the examples folder, you'll find hello-world.dtms. I'm going to step through and explain what's happening there.

So first we define a 'message' type of size 14 bytes:

`# message 14`

Then we fill the data from 10 to 10 + 14 - 1 or 10 to 23 with "\n!dlrow ,olleH" (backwards because the algorithm subtracts fyi). Note how they're all in ascii's decimal

`(10 : message) = 10 33 100 108 114 111 119 32 44 111 108 108 101 72;`

Now, you might ask, why 10? Well that's because 0-9 are all special memory locations. Location 0 is program input. Location 1 is program output. And locations 2-9 are a long representing instruction points. Note, and instruction point IS NOT the same as a line NOR a token. Instructions consist of one of the 4 above.

So the first instruction was the typdef, that's program counter == 0. The second is setting 10->23. That's 1. This is 2:

`(24 : char) = 23;`

We set the byte just after the string to have a *value* that's the *address* of the end of the string.

Moving on, we pause assignments for that duration:

`! (24 : char)`

Now here's where this algorithm gets tricky. If you notice, we only have 9 resumes: `>>>>>>>>>`. 9 resumes is *not enough* to resume execution, so the next assignment right after: `(2 : long) = 00 00 00 00 00 00 00 30;`, is skipped! We'll revisit this in a second.

Moving on, we have the other skips that we need: `>>>>>>>>>>>>>>`, which resume assignment execution.

So then, we write a *double-address* to output: `(1 : char) = [24 : char];`. Now, the difference between an address and a double address is really simple. If you put parentheses and a number, you get the value at an addres. If you put brackets and a number, you get the value at the memory location pointed to by the value of the number. So it's like doing double the address: `( ( # ) ) === [ # ]`. So we get the value at location 24, which is currently 23, and then get the value at 23, which is currently 72 or 'H'. We then output that.

Next, we decrease our value at address 24 that we've been keeping up with, so it's now 22: `(24 : char) -= 1;`.

And finally, we set location 2 to be 2 (but as a long). Like I said before, 2 is the program counter, so we're making a jump using assignments up to instructions 2. Instruction 2 is `(24 : char) = 23;`, but after we jump, the program counter increments again, so we're actually jumping to instruction 3, which is setting pause again.

Just like that we have a loop. Have you figure out what happens, yet? As we decrease the value at address 24, we move backwards along our backwards string array, outputting the characters as we go. When we get to the last character, address 24 has a value of 9. So we pause for 9, which means this time, we don't skip the instruction on line 7.

This instruction, `(2 : long) = 00 00 00 00 00 00 00 30;`, sets the program counter to the last instruction, which, because of increasing, actually jumps us to the end of the program, and ends it, with "Hello, world!\n" printed in the terminal.

It's a mess, but it's my mess :)
