Aspartame Scale — Activity Runbook

Activity name: Scale
Purpose: A general-purpose typed quantity scaler and unit converter.

Scale takes a list of quantities and applies a common scale factor to the entire list. The scale factor can be selected directly, derived from a desired output quantity, or calculated from the amount of an item available.

Recipes are an obvious use case, but Scale must remain general-purpose.

Core Concept

A Scale object is a typed quantity list.

Example:

Chocolate Cake

Flour       2       cup       volume
Sugar       1.5     cup       volume
Butter      8       oz        mass
Eggs        3       each      count
Milk        1       cup       volume
Vanilla     2       tsp       volume
Oven        350     °F        temperature

Makes: 12 servings
Scale: 100%

Every item has:

Name
Value
Unit
Type
Scaling behavior
Optional conversion information

The important distinction is:

Numbers have meaning.

8 oz butter is an amount that should scale.

350 °F oven is a setpoint that can be converted between °F and °C but should NOT normally become 175 °F when making a half batch.

Primary Scaling Model

There is exactly one authoritative scale factor for the object.

Multiple interactions can determine it:

Percentage ─────────────┐
                       │
Target output ─────────┼──→ SCALE FACTOR ──→ Entire list
                       │
Available ingredient ──┤
                       │
Maximum possible ──────┘

Changing one method updates the others.

Example:

Original makes: 12
Desired:        18

Scale:          150%

All scalable quantities become 150% of their originals.

Scale Slider

The simplest interaction is a percentage slider.

Scale

25% ───── 50% ───── 100% ───── 200%
                     ●

100%

Moving it immediately updates the list.

Example:

100%

Flour      2 cups
Sugar      1 cup
Eggs       3


50%

Flour      1 cup
Sugar      1/2 cup
Eggs       1.5

Do not require an Apply button.

Scaling should feel continuous and direct.

The exact percentage should also be editable numerically for values difficult to select with the slider.

Make Quantity

A Scale object may optionally define an output quantity.

Example:

Makes: 12 muffins

The user can request:

Make: 30 muffins

Scale calculates:

30 / 12 = 2.5

Scale: 250%

The complete list updates automatically.

The user should not need to calculate the percentage manually.

Output units can be arbitrary:

servings
muffins
loaves
assemblies
batches
liters
panels
kits
bricks
Make To Available Amount

Any scalable item can become the basis for the scale.

Example original:

Flour
2 cups

User says:

I have: 1.37 cups

[Make to this amount]

Scale calculates:

1.37 / 2 = 0.685

Scale: 68.5%

The entire list updates to 68.5%.

This is a first-class interaction, not a recipe-specific feature.

Limiting Quantity / Maximum Possible

Users may optionally enter available quantities for multiple items.

Example:

              Needed       Available

Flour         2 cups       4 cups
Sugar         1.5 cups     1 cup
Butter        8 oz         2 lb
Milk          1 cup        1 gal

Scale can determine which available quantity imposes the lowest possible scale factor.

Sugar is limiting.

Maximum scale: 66.7%

Then:

[Make Maximum]

sets the entire Scale object to that factor.

Conceptually:

available quantity / original quantity

is calculated for every compatible constrained item.

The smallest resulting factor is the limiting quantity.

Do not describe this internally as a mathematical "least common denominator." The user-facing concept is:

What is the largest complete amount I can make with what I have?

Typed Quantities

Units belong to semantic types/dimensions.

Initial types should include:

Quantity
│
├── Count
│   ├── each
│   ├── pair
│   └── dozen
│
├── Mass
│   ├── mg
│   ├── g
│   ├── kg
│   ├── oz
│   └── lb
│
├── Volume
│   ├── mL
│   ├── L
│   ├── tsp
│   ├── tbsp
│   ├── cup
│   ├── fl oz
│   ├── pint
│   ├── quart
│   └── gallon
│
├── Length
│   ├── mm
│   ├── cm
│   ├── m
│   ├── in
│   ├── ft
│   └── yd
│
├── Temperature
│   ├── °C
│   ├── °F
│   └── K
│
├── Time
│   ├── ms
│   ├── second
│   ├── minute
│   └── hour
│
└── User-defined
    ├── bag
    ├── bucket
    ├── scoop
    ├── sheet
    └── etc.

The type determines which conversions are valid.

Unit Conversion

Scale performs conversions only between compatible dimensions.

Valid:

cup  ↔ mL
L    ↔ gal

oz   ↔ g
lb   ↔ kg

in   ↔ mm
ft   ↔ m

°F   ↔ °C

dozen ↔ each

Invalid:

cup → grams
meters → liters
pounds → gallons
°F → ounces

Scale must never silently perform a dimensionally invalid conversion.

Ambiguous Units

Units must have explicit dimensional identities internally.

For example:

oz

is ambiguous to humans.

Internally these must be distinct:

ounce_mass
fluid_ounce_volume

The UI may display:

oz
fl oz

but the data model must never confuse them.

Item-Specific Conversion Bridges

Some conversions require knowledge about the particular item.

Example:

Flour

1 cup = 120 g

This permits:

2 cups flour → 240 g flour

But that relationship applies to Flour, not universally to the cup unit.

Another item may define:

Butter

1 cup = 227 g

Therefore:

Volume-to-mass conversion is item-specific, never globally inferred.

Users may optionally provide these bridges.

Scaling Behavior

Each item has a scaling behavior.

Initial behaviors:

SCALE
Value changes with global scale.

FIXED
Value remains constant.

DERIVED
Value follows some defined relationship.

OPTIONAL
Informational/optional quantity.

Example recipe:

Flour       2 cup       SCALE
Butter      8 oz        SCALE
Eggs        3 each      SCALE
Oven        350 °F      FIXED
Bake        30 min      FIXED

At 50%:

Flour       1 cup
Butter      4 oz
Eggs        1.5 each
Oven        350 °F
Bake        30 min

This prevents Scale from treating every number as a multiplicative quantity.

Discrete Quantities

Some quantities cannot practically exist as arbitrary fractions.

Example:

Eggs
Original: 3 each

Scale: 50%

Exact: 1.5 eggs

Scale should preserve mathematical truth rather than silently rounding.

It may additionally offer:

Exact:      1.5 eggs
Practical:  2 eggs

But rounding must never silently change the scale factor for the rest of the list.

Future versions may support constraints such as:

Whole units only
Nearest 0.5
Nearest package
Minimum 1
Multiples of 6
Fractions and Human-Friendly Display

Scale should avoid ugly machine-oriented results where reasonable.

Instead of:

0.333333 cup

prefer:

1/3 cup

Instead of:

0.0625 cup

consider a better compatible unit:

1 tbsp

The exact underlying numeric value must remain authoritative.

Display formatting must not introduce cumulative rounding errors.

Display Unit Modes

Possible display preferences:

Original Units
Metric
US Customary
Best Fit
Original Units

Preserve units entered by the author.

Metric

Prefer appropriate metric units.

US Customary

Prefer appropriate customary units.

Best Fit

Choose a compatible unit that produces a convenient human-readable value.

Example:

0.03125 gallon

could display as:

4 fl oz

Best Fit should prioritize usability rather than merely selecting the mathematically largest/smallest unit.

General-Purpose Use

Scale must not contain assumptions that everything is food.

Example:

Concrete Mix

Cement       4 bag
Sand         12 bucket
Water        8 L
Pigment      400 g

Scale: 250%

Result:

Cement       10 bag
Sand         30 bucket
Water        20 L
Pigment      1 kg

Other expected applications include:

recipes
construction mixtures
paint
craft materials
fabrication
model making
inventory kits
BOM quantities
gardening mixtures
photography processes
3D printing materials
classroom ratios

Domain-specific extensions can come later.

User-Defined Units

Unknown units should not prevent scaling.

Example:

Sand       3 bucket
Cement     1 bag

Scale doesn't need to know what a bucket contains to calculate:

200%

Sand       6 bucket
Cement     2 bag

However, Scale must not invent conversions for those units.

Users may optionally define relationships later:

1 bag = 25 kg
Sugar Integration

Scale is a Sugar Activity.

Its interface should remain focused on:

Title
Quantity list
Scale
Result

Avoid turning it into spreadsheet software.

A saved Scale object belongs naturally in Journal:

Scale

Pizza Dough
Makes 7 pizzas
175%

Today

Resuming restores the complete typed quantity list and current scale.

Data Model

Conceptually:

Scale Object
│
├── title
├── original_output
├── current_scale
├── display_unit_preference
│
└── items[]
    ├── name
    ├── original_value
    ├── dimension/type
    ├── unit
    ├── scaling_behavior
    ├── available_quantity
    ├── rounding/display preference
    └── optional conversion bridges

Original values remain authoritative.

Never repeatedly scale already-scaled values:

WRONG:

100% → 75% → 50%
        ↑
scale the previous result

Always calculate:

displayed value =
original value × current scale factor

This prevents accumulated floating-point/rounding errors.

MVP

Version 1 should implement:

Create a named Scale object.
Add/remove/reorder items.
Give each item a value.
Assign a type/dimension.
Assign a compatible unit.
Mark items SCALE or FIXED.
Change global scale percentage.
Set scale by desired output quantity.
Set scale from one available item.
Calculate limiting item from multiple available quantities.
Convert common compatible units.
Display sensible fractions/units.
Save/resume through Journal.
Undo/redo.

Keep the interface extremely small.

Explicit Non-Goals for MVP

Do not initially add:

nutritional calculations
calorie databases
grocery shopping
recipe websites
cloud accounts
inventory databases
barcode systems
chemistry simulation
automatic density guessing
AI ingredient interpretation
spreadsheets
costing
supplier management

These can be considered later without contaminating the fundamental Scale model.

Design Laws

One authoritative scale factor.

Original quantities are immutable reference values during scaling.

Every numeric quantity has semantic meaning.

Units belong to dimensions/types.

Only compatible dimensions convert automatically.

Conversion and scaling are different operations.

Temperature/setpoints do not scale merely because they contain numbers.

Unknown units may scale without being convertible.

Item-specific conversion knowledge stays item-specific.

Never silently round away mathematical truth.

Never silently invent unit relationships.

Recipes are a use case, not the architecture.

Keep the surface simple; expose deeper capability progressively.

One-Sentence Specification

Scale is a Sugar Activity for building typed quantity lists and applying one common scale factor to them, with automatic compatible-unit conversion and the ability to derive that scale from percentage, desired output, available quantities, or the limiting item.

MVP Success Test

Someone enters:

Pizza Dough
Makes 4 pizzas

Flour       1000 g
Water       650 mL
Salt        25 g
Yeast       7 g
Oven        475 °F

They discover they have only:

Flour: 730 g

They select Make to this amount.

Without doing arithmetic themselves, Scale produces:

Scale: 73%

Makes: 2.92 pizzas

Flour       730 g
Water       474.5 mL
Salt        18.25 g
Yeast       5.11 g
Oven        475 °F

The user can then change units, choose a practical target, or continue adjusting the scale without destroying the original quantities.

If that interaction is immediately understandable without explaining dimensional analysis, the Activity works.