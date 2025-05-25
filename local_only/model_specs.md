Software Engineering Dev Ops Case Studies


Context:

Working on a 3D Game 

Problem: 


3D files were supplied in the wrong format, so they needed to be replaced later.
Models in 3D files were the incorrect scale, leading to rework.
Issues with models were not identified immediately. The issue would be identified later by an engineer who would relay the message to the 3d modeler and provide instructions on how to fix it. For scale issues, the modeler didn’t have a specific size they were targeting, so they needed the engineer to tell them what scale % to change their model. 
Root cause: 3D Modelers didn’t have a specific measuring scale in their 3d modeling program. Sometimes, there was not a specific size specifications for models.
Sometimes, 3d model mesh, UV mapping, materials, textures, rigging, and animations are not all on the model at the same time and are sometimes delivered in different formats at different times. They are connected in the engine. This removes some of the ability for modelers and animators to preview more complete work in their own modeling programs such as blender and maya. As a result, engineers were tasked with combining meshes, animations, and creating correct materials in the engine. This required engineers to have a more detailed understanding of each specific model and its needs and the specifications and expectations for any model. This also separated those doing the work (modelers, animators) from the final work product (a modeled, textured, rigged, animated model). This resulted in a software engineer acting as a go-between for modeling, texturing, and animation work because the software engineer was the one comfortable in the engine.

Root causes:



* There was a not a defined process for 3D modelers to follow
  * There wasn’t always a specific defined model specifications
    * filename of the model
    * directory path of the model
    * 3d Scene root node name
    * Unit of measurement (meters)
    * Dimension
    * Identity transform on root node.
    * Up facing direction after export. (Y up)
    * Model front-facing direction after export. (Z forward)
    * If it has UV mapping or not
    * If it has textures or not
      * What textures specifically to include
        * filepath
        * type (diffuse, normal, specular, etc.)
    * If it is rigged or not. (has bones or not)
    * What animations specifically to include
      * name
      * in-place
      * looping
    * If it has blend shapes or not
  * 3D modelers didn’t have a specific measuring scale (meters) in their 3d modeling program
  * 3D modelers were using a different scale (centimeters) than what was needed for the game engine (100x scale difference)
  * 3D modelers used the incorrect export settings
    * Up direction was incorrect. (Was Z up instead of Y up)
    * Exported in the wrong format (FBX, GLB instead of GLTF)
  * Had unapplied transformations (scale, rotation, position)
* 3D modelers didn't know what to evaluate of their work.
  * They didn't know how to check model size.
  * They didn't know how to export in GLTF format
  * They didn't have a way to export gltf from Maya
    * They didn't have the plugin required to export in GLTF format (Maya)
* 3d modelers were unfamiliar with GLTF file format
  * They didn't know what GLTF was.
  * They didn't understand the benefits of GLTF.
  * They didn't know that GLTF would output more than 1 file for a model. (gltf + bin)
* 3D modelers did not have a specific process to evaluate their own work in Godot Engine.
  * 3D modelers were unfamiliar with Godot Engine
  * 3D modelers did not know how to evaluate their own work in Godot Engine
  * 3D modelers did not review their work in Godot Engine
* 3D modelers had never used Godot Engine before.
* 3D modelers did not know how to import models using Godot engine.
* 3D modelers did not know where models should be saved.