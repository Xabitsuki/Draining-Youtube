## Introduction

YouTube is today the largest video sharing platform.  
In 2019, it counts more than a billion of users, more than 7 billion videos and more 
than 300 hours of video are uploaded each minute.  Nowadays, smartphones, drones, board cameras, 
dash camera have become common and more
content is produced everyday an uploaded on the platform, making it an almost inexhaustible
source of videos of our world.  
_But how could this impressive database be exploited?_  

Using photogrammetry  techniques,  it  is  possible  to  extract  from  a  series  of  pictures,
the  3D  structure  of the photographed scene.  To do so, a set of different frames of the same 
subject photographed on different angles
is processed and a geometric model of the subject is generated.


Numerizing the world has become one of the challenges of the 21st century, and combining
YouTube and photogrammetry could be an affordable solution.
Indeed, instead  of  having  to  invest  huge  amounts  of  money  to  numerize  the  world
that  surrounds  us,  why  don’t we recycle the content of YouTube to generate 3D models 
of the world?  
This questions motivated this study.  

The  goal was to  see  if  the  material  available  for  free  on  the  platform  could 
be  used  to  generate  sparse  3D model.
A positive answer implies that an enormous database representing many locations around 
the globe is  accessible  without  the  need  of  new  numerization  campaigns  and  all  
the  costs  related.
The  generated models could be shared freely and could track the evolution of the 
surface of the globe as many places are recorded several times.


## Research summary

To investigate the question of wether or not YouTube can be used a source for the generation
of 3D models of the world, a __draining__ pipeline was implemented. 

##### Pipeline summary
The pipeline was required to takes as __input__ a link to a YouTube video and to
__output__ the 3D models generated from the video. 

The pipeline realizes the following tasks: 
1. Provided a link to a YouTube video such as this 
[footage of Lausanne shot by a drone](https://www.youtube.com/watch?v=LnyKeqdzQao),
the video is downloaded. (realized using `youtube-dl`)
2. Frames are extracted at a constant rate (say 2 frames are extracted for 1 second of 
video). (realized using `ffmpeg`)
3. The extracted frames are used to reconstruct the 3D structure of the recorded scenes. 
(realized using the `openMVG` library)  

When the pipelien finishes, `set_X/` (X is an index) files were generated, each one containing 
the frames that were used to generated the a 3D sparse point-cloud model 
of the scene. 
##### Illustrations
Consider the following frame of Lausanne's cathedral. 
![alt text][cathedral]

Using the draining pipeline one can generate a 3D sparse model that looks like: 
![alt text][model] 

Where the green points are the estimated camera poses. 

[cathedral]: imgs_readme/frame0093.png
[model]: imgs_readme/cathedral_lausanne_3d01.png

## Installation and Usage

#### Dependencies: 
##### Python
The pipeline is basically a python wrapping that orchestrates calls to 
the external libraries.
The code is written in python 3 and installing jupyter notebook is also required 
to execute the notebooks provided.  
Both can simply be installed by downloading the Anaconda distribution that can be found 
at this [link] (https://www.anaconda.com/distribution/) (select python 3.XX distribution).

##### External librairies
The draining pipeline uses three main components: `youtube-dl`, `ffmpeg` and `openMVG`. 

To install the latest versions of `youtube-dl` and `ffmpeg` please refer to the 
following links:
- [install youtube-dl](http://ytdl-org.github.io/youtube-dl/download.html)
- [install ffmpeg](https://ffmpeg.org/download.html)

The actual version of the pipeline uses a slightly modified of openMVG:
some lines of the source code were modified for convenience and the 
the pipeline uses the __develop__ branch of openMVG (time of writting: 3rd of July 2019). 

The used version is provided in the folder [openmvg_folder].
To install openMVG, simply follow the installations instructions provided on the 
openMVG [github](https://github.com/openMVG/openMVG/blob/master/BUILD.md).

We recommend installing MeshLab for the visualization of the 3D models: available 
[here](http://www.meshlab.net)
 
[openmvg_folder]: openMVG_develop/
 
##### Test the installation 

After installing all the dependencies, the `drain_one.py` script can be run 
to download and process the aforementioned drone footage of Lausanne. 
To do so, open a terminal in the `scripts/` folder and execute:  
`$ python drain_one.py`

The output of `youtube-dl`should be displayed  in the terminal, followed
by those of the `ffmpeg` and the `openMVG`. 

The executions can take about 5 minutes.  
Once it finished, in the `videos/` folder one can find the `test_video/` folder. 
In `test_video/` there is a folder named using the YouTube ID of the downloaded video which
is the `LnyKeqdzQao/` in this case.  

In `LnyKeqdzQao/`:
- `data/` contains the video file and descriptive file.
- `frames/` contains the images that the program discarded and did not use in any of the 
generated 3D models.
- `iter0/` contains files generated during the process. 
- `sets/` can contain one or several `set_X` folders.
In each:
    - `frames/` folder containing the frames used for the 3D reconstruction.  
    - `features/` folder and the `sfm_data.json` file are data used by openMVG in the reconstruction.  
    - The 3D model can be found in the folder `incremental/` and is generically named 
`sfm_data_color.ply` for each set (can be opened using MeshLab).

If the installation and the process succeeded you should have the same point cloud model
of Lausanne's cathedral as showed above. 

Have fun !
 

## License

MIT License

Copyright (c) 2019 Xabier Rubiato

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
