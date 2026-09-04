=====
Count
=====

Count is a hands-on Activity for building and measuring a small voxel model.
A voxel is a cell with a position in a grid and a layer in depth. You can use
Count for arithmetic, patterns, simple diagrams, floor plans, or any question
where “how many?” is easier to answer by making the object.

The Count screen
----------------

The large canvas is a grid of cells. An empty cell is a place where a voxel can
be added. A filled cell is drawn as a cube with a top and side face so the depth
of the model is visible. The large number above the canvas is the total number
of filled cells across every layer.

The **EDIT LAYER** rail beside the canvas tells you exactly which plane is
editable. It shows:

* the current layer number and total layer count;
* the number of voxels on the selected layer;
* **Back layer** and **Forward layer** arrow controls;
* buttons to create or copy a layer;
* a direct **Delete layer** button for removing the selected plane.

Only the selected layer is editable. Other layers remain visible as quiet,
translucent cubes behind it. This lets you align a new layer with an existing
shape without accidentally changing the wrong plane.

Making and removing voxels
--------------------------

Click an empty cell to add one voxel. Click a filled cell to remove it. Drag
across empty cells to paint a group of voxels quickly. The selected plane has a
strong outline and a light grid; use that outline as the editing boundary.

The total updates immediately. “On this layer” counts only the selected plane,
while the large total counts every plane. Comparing those two numbers is a
simple way to check a calculation.

Working with layers
-------------------

Layers are ordered from the front of the model toward its depth. Use **Back
layer** to edit the adjacent plane behind the current one, and **Forward
layer** to move toward the front. The layer number remains visible while you
move, so “Layer 2 of 4” always means the second editable plane in a four-layer
model.

* **New layer** adds an empty plane behind the selected layer.
* **Copy layer** adds a duplicate of the selected plane behind it.
* **Delete layer** removes the selected plane. Count keeps at least one layer.

The cubes are drawn from the deepest plane toward the selected plane. The
selected plane is drawn last with a stronger outline, so it stays clear and
editable even when several layers contain matching cells.

A practical counting exercise
-----------------------------

1. Start with the empty grid and fill three cells.
2. Confirm that the layer count says three on this layer and the total says
   three.
3. Create a new layer and fill two cells. The layer total becomes two and the
   overall total becomes five.
4. Move between layers with the arrows and compare the translucent shapes.
5. Copy a layer, then remove one voxel from the copy. The copied layer now has
   one fewer voxel while the original remains unchanged.
6. Stop the Activity and resume it from the Journal to verify that the model
   and selected layer were saved.

Undo, Journal, and safe experiments
-----------------------------------

Count records each click, drag gesture, and layer operation as an undoable
change when undo support is available in the Activity toolbar. The Journal
stores the grid dimensions, every layer, and the selected layer number. Stop
normally so the latest model is written before the Activity exits.

For experiments, copy a layer or duplicate the Journal entry before making a
large change. Deleting a layer changes the model; it does not delete unrelated
Journal entries or remove the Count Activity itself.

How Count represents a model
----------------------------

Internally, Count stores a list of two-dimensional Boolean grids. Each grid is
one depth layer; each ``True`` cell is a voxel. The total is the sum of all
``True`` cells. The selected layer index controls both the edit target and the
strongly highlighted plane. Cells within a layer stay aligned. The renderer gives each layer a shallow,
consistent depth offset, paints deeper layers first with reduced opacity, and
paints the selected layer last so the stack reads as 3D without becoming a
staircase.

This representation is deliberately small and inspectable. It makes a useful
bridge from physical cubes to arrays, coordinates, loops, and three-dimensional
programming.

Troubleshooting Count
---------------------

* If a click changes the wrong place, check the highlighted editable plane and
  its layer number before clicking again.
* If a cube seems to disappear, move to the adjacent layer; it may be a quiet
  voxel behind the selected plane.
* If the total is unexpected, compare “on this layer” with the overall total
  one layer at a time.
* If the model is not restored, stop the Activity normally and check the
  Journal entry rather than deleting it.

Count is a model-making Activity: build a hypothesis, count it, change one
layer, and compare the result.
