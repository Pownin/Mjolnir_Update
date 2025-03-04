# Mjolnir_Update
I am expanding the blender tool in Halo 3 to more maps. Currently the tool supports. 

- Assembly
- Avalanche
- Blackout
- Citadel
- Construct
- Edge
- Epitaph
- Foundry
- Ghosttown
- Guardian
- Icebox
- Last Resort
- Longshore
- Narrows
- The Pit
- Rats Nest
- Sandbox
- Sandtrap
- Standoff
- Valhalla
- Waterfall

**FEATURES**
- Import / Export Objects to and from game
- Utilize channels larger than 10 and any spawn time between 0-255
- Spawn objects in an array
- Prefabs
- "Toggle Physics". Pressing this will enable the game to spawn all objects as phased automatically (Sometimes doesnt work right)
- "Optimize Selected". When importing a prefab if you select those objects and any default map pieces available it will attempt to replace the imported ones with the default one
- Now works on 21 maps

**Limitations**
- After a few exports the map will start acting weird. No need to panic just save your map and load back into it. Use the "Refresh Objects" button when you load back into the map.
- Halo 3 is very easy to crash. If you do anything wrong the game will crash. Save your map often. 
- DO NOT TOUCH ANYTHING IN THE RIGHT OUTLINER OF BLENDER. THE ORDER MUST REMAIN HOW IT IS.

**TIPS**
- If you duplicate a default object you will need to go to the forge tab while the duplicated object is selected and untick the "Scenario Object Bit" flag and tick "Object Edited" before you export to the game. 
- I added a button called "Walk Navigation" it will allow you to free fly in blender. To increase speed scroll forward on your mouse wheel to decrease scroll backward.

**REQUIREMENTS**
- So far this tool has only worked on blender versions 4.0 and higher. It was tested on 3.5 and it crashed. It may work on other versions though. 
- Easy Anti Cheat must be off. I have tested on both the steam and windows version of MCC and it works on both. 

**GETTING STARTED**
1. Download the latest release
2. Extract all the contents of the zip to the same folder. It shouldn't matter what folder just keep all the files together.
3. Follow the video for basic usage information.

**Brief Tutorial**

https://www.youtube.com/watch?v=bnRqn_kbU0w

**CREDIT**
This tool was not created by me. This tool was originally created by Waffle1434 for Halo Reach then converted to work with Halo 3 but ExhibitMark. I am just adding new features to the 
tool and updating it to work with more maps. 

Thank you Daylon for helping me create the MemoryScanner to dynamically find the correct address. 



The actual .blend files will not show in the repo as they
are to large to upload. Just the code will show here.

This tool should continue to work through new game updates. It gets the address from the tls so game updates shouldnt break it.
