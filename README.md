<h1>textedit-u1380611</h1>

## Quick Start

```bash
# Clone the repository
git clone https://github.com/peytjensen/textedit-u1380611.git
cd textedit-u1380611

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python textedit.py
```

<p><h2>R1</h2></p>
<p>
For this first release, I successfully implemented all the basics such as text editing, selection, keyboard shortcuts, and a menu bar. My approach was to ask ChatGPT to break down the entire control flow of Microsoft Notepad into simple actions such as File > Save as > File explorer popup. This worked incredibly well and I had all of these basics implemented in less than 3 prompts. I also have implemented an unsaved changes popup when closing a file you have modified and I have started on tabs/split view, although that feature won't be ready till next release.
</p>
<p>
For testing I have an AMP-generated testing suite that currently includes 90 tests. These test various functions such as file read/write, UTF-8 encoding, errors, document modeling, word wrap, etc. I plan on implementing more tests as I continue with the project, so far the tests AMP has made look correct and I haven't felt the need to edit them. AMP also does surprisingly well with modularity on it's own, and many components such as document handling, the editing pane, the file handler, and more, have all been split into their own files without the need of my instruction. Moving forward, as mentioned above, I have started on a tab and split view system that I will refine in the next release along with adding new features. 
</p>
<img width="275" height="241" alt="image" src="https://github.com/user-attachments/assets/511ae3d2-a5c9-4454-8663-606a08d3d907" />

<p><h2>R2</h2></p>
<p>
This week I added and refined the tabs system and split view, along with adding a few themes. The tabs and split view are very smooth at this point and work very well. Dragging and rearranging tabs, along with dragging a tab to either half of the screen to create a split view is pretty seamless. Another thing I am very happy with is the resizing of the split view windows. One thing that does not work as smoothly is dragging a tab that is in split view back to the original tab bar in order to collapse back into one view. It works, but you have to go down and around the secondary tab bar rather than dragging directly horizontal. As of now, I have unit tests for every function I have added. I made a note in my AGENTS.md to always write tests for new code and run/debug them before reporting back to me and this has worked well so far. 
</p>
<img width="400" height="350" alt="image" src="https://github.com/user-attachments/assets/a253552e-6e1c-432f-8024-7a76fbd8ef8c" />

<p><h2>R3</h2></p>
<p>
For this final week, I have implented a theme and font editor pane where you can create and save new custom themes, along with apply fonts to a full document or selected text. I also added a floating toolbar, similar to Microsoft Word, where when you select text you can change the font and size inline. I am proud of this feature because it works very well and I had to do a lot of adaptation to get the text size to work on my system. I am using hyprland on linux which is built on the wayland protocol, this protocol handles window focus differently than most, and it took a lot to get it so that you can actually type in the font size box (rather than behind it). I also added a file tree explorer for an extra feature, it is accessed by selecting "open folder". It works pretty well, and allows for the opening of files in new tabs. One thing I could not get to work perfectly for this is making the collapsing smoother, you can collapse and hide it, it's just pretty clunky. Finally, I added unit tests for all of these new functions, and they all are working. The AGENTS.md file has been extremely useful, as AMP will always write tests and squash bugs before reporting back to me. 
</p>
<img width="405" height="320" alt="image" src="https://github.com/user-attachments/assets/eaee89a5-d3cb-4cc4-8bbb-9cceb5c4254c" />
<img width="305" height="320" alt="image" src="https://github.com/user-attachments/assets/3ae58e0b-f0ce-4c42-bd66-e6614e1ee963" />
<img width="730" height="360" alt="image" src="https://github.com/user-attachments/assets/01cf943e-438d-4f65-9643-14d0ca13ec74" />
<img width="650" height="500" alt="image" src="https://github.com/user-attachments/assets/d53fedec-a01c-4ee3-b847-5190f1e3fe4a" />



