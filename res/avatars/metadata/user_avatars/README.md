## Metadata ```user_avatars``` folder info

This folder is used to store generated avatars for every user. </br>
The purpose of this is to trade memory usage for CPU and not having to re-generate avatar every time it is requested/needed.</br>

### Few notes: </br>
The format of avatars is ```.png``` </br>
Whenever a new user starts to use the bot, the default avatar for his ```user_id``` will be generated and stored here.</br>
Whenever user changes his avatar details, the new avatar will be immediately re-generated and stored here overwriting the old one. </br>

Obviously, there is a room for improvement to this approach but for now it is what it is.
Some things that can be done: </br>
- Make this approach optional
- Do not re-generate default avatar (for ex. for new users) and use stored one (could have some downsides)
- Perhaps make a limit to possible amount of stored pictures (memory to CPU trade is good until you run out of it...)
