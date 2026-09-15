Aspartame Count — Feature Runbook

Working Activity name: Count
Purpose: A deliberately simple voxel/grid multiplication tool for visually counting regularly arranged physical objects, especially inventory.

Core concept

Start in 2D.

The user draws the physical arrangement they see by toggling cells on a grid:

■ ■ ■ ■ ■
■ ■ ■ ■ ■
■ ■ ■ ■ ■
■ ■ ■ ■ ■

5 × 4 = 20

Each filled cell represents one object.

To represent depth/height, the user adds layers. Each layer is another editable 2D grid.

Layer 1     20
Layer 2     20
Layer 3     18

Total       58

The application derives the 3D voxel structure from those layers.

Primary interaction is editing 2D layers. 3D is visualization, not the primary editor.

Primary workflow

For inventory:

New Count
   ↓
Set/expand X × Y grid
   ↓
Tap cells to represent objects
   ↓
20 objects on Layer 1
   ↓
Duplicate Layer
   ↓
Inspect physical next layer
   ↓
Remove missing objects
   ↓
Repeat
   ↓
Total: 137

This should be faster than manually counting every object.

Example

A pallet has five cases across and four deep.

Layer 1

■ ■ ■ ■ ■
■ ■ ■ ■ ■
■ ■ ■ ■ ■
■ ■ ■ ■ ■

20

Duplicate twice.

Layer 3 is missing two cases:

Layer 3

■ ■ ■ ■ ■
■ ■ ■ ■ ■
■ ■ ■ ■ ■
■ ■ ■ · ·

18

Result:

Layer 1       20
Layer 2       20
Layer 3       18
────────────────
Total         58

When layers are identical, also show the multiplication naturally:

5 × 4 × 3 = 60

When irregular, don't force a misleading multiplication expression. Show the layer counts and actual total.

Controls

Keep v1 extremely small:

Toggle voxel/cell
Expand/shrink X dimension
Expand/shrink Y dimension
Previous layer
Next layer
Add layer
Duplicate layer
Delete layer
Clear layer
Undo/redo
Total count
Save/resume

Grid editing should work with mouse, touch and keyboard where practical.

Do not require 3D controls to perform a count.

Layers / Z axis

Z is represented primarily as a stack of pages:

        Layer
     ◀   3 / 7   ▶

       Duplicate
       + Layer
       − Layer

Moving between layers should be immediate.

Duplicate Layer is especially important for inventory because physical stacks commonly repeat.

3D visualization

Provide an optional simple isometric voxel preview.

It should automatically reflect the layer data:

          ■ ■
        ■ ■ ■
      ■ ■ ■ ■
    ■ ■ ■ ■
  ■ ■ ■ ■

Its purpose is answering:

“Does this look like the stack in front of me?”

Initially, it should not become a CAD/voxel editor.

No Minecraft camera controls are required for MVP. If rotation is eventually added, keep it constrained and obvious.

Sugar integration

This is a Sugar Activity, preferably named Count.

The name describes what the user does rather than its implementation.

A saved Count becomes a resumable Journal object:

📦 Back room soda

Count
137 objects

Last worked on today

Resume restores:

grid dimensions
every layer
voxel positions
current layer
optional title/description

The underlying data should remain small and portable.

Data model

Conceptually:

Count Object
├── title
├── width
├── height
├── layers
│   ├── layer 1
│   │   └── occupied cells
│   ├── layer 2
│   │   └── occupied cells
│   └── ...
└── metadata

Do not store rendered screenshots as authoritative state.

The voxel/layer representation is authoritative; visualizations are projections of it.

A compact JSON-like representation would be perfectly adequate initially.

Multiplication behavior

The application should teach/show multiplication naturally without requiring the user to formulate the equation.

For a complete rectangle:

5 × 4 = 20

For three identical complete layers:

5 × 4 × 3 = 60

For irregular arrangements:

Layer 1    20
Layer 2    20
Layer 3    18

Total      58

Never claim 5 × 4 × 3 represents the actual count when voxels are missing.

Design philosophy

This should feel like a physical manipulative, not spreadsheet software.

The fundamental operation is:

I see an object → I put a square there.

Then:

I see another level → I add a layer.

The mathematics emerges from the representation.

This makes the same Activity useful for:

inventory
pallets
shelving
crates
cans/bottles
boxes
tiles
blocks
classroom multiplication
volume/counting demonstrations

Don't create separate “education” and “inventory” modes initially.

Explicit non-goals for v1

Do not add:

textures
arbitrary voxel colors
physics
free-form 3D construction
perspective camera controls
CAD functionality
spreadsheets
barcode scanning
inventory databases
SKUs
prices
warehouse management
accounts/cloud sync

Those may be interesting later, but they obscure the core interaction.

Future possibilities

After the core interaction proves useful, possible additions include labels/categories, multiple object types, constrained 3D rotation, measurement/dimensions, CSV export, barcode association, camera-assisted counting, and sharing a Count object through the Neighborhood Board.

But Count should remain useful without any of them.

One-sentence specification

Count is a Sugar Activity where users represent physical objects as voxels by drawing editable 2D layers, while the Activity automatically calculates per-layer and total counts and optionally projects those layers into a simple 3D visualization.

MVP success test

Put 58 real boxes in a roughly rectangular stack in front of somebody who has never seen Count.

If they can open the Activity, reproduce the stack as layers, and arrive at 58 without needing instructions about “voxel editing” or “3D modeling,” the design works.