# **Needs & Status System**

* **Status Meters (float):**  
  * Food 0 \-\> 1  
  * Cleanliness 0 \-\> 1  
  * Social 0 \-\> 1  
* **Status Meter tiers (float):**  
  * Food  
    * Overfed (more than 0.6)  
    * Full (0.5-0.6)  
    * Hungry (0.3-0.5)  
    * Starving (0 \- 0.3)  
  * Cleanliness  
    * Clean (0.7- 1\)  
    * Dirty (0.4-0.7)  
    * Filthy (0 \- 0.4)  
* **Status Flags (Booleans):**  
  * `is_hungry`, `is_dirty`, `is_lonely`, `is_overfed`,  
* **thresholds/Timers:**  
  * Each value ticks down at an independently defined rate.  
    * Cleanliness\_down\_rate  
      * When poo (faster)  
    * Food\_down rate  
    * social\_down\_rate  
* **Flag Manager:**  
  * Detects which flags are currently active and exposes them to the lifecycle system.

# **Interaction System**

* **Feed:** Drag food to pet, adjusts hunger.  
* **Pet:** Click interaction to increase social, clear loneliness.  
* **Clean:** Click poop to remove it and reset `is_dirty`.

# **Pet Lifecycle System**

* **Lifecycle Clock:** Triggers aging at fixed intervals.  
* **Age Tracker:** Increases each tick, represents score.  
* **Lifespan Limit:** Base lifespan minus total accumulated **lifespan debuff**.  
* **Tick Processing:** On each tick:  
  * Apply debuff if any negative flags are active.  
  * Check for death condition.

#  **Permanent Lifespan Debuff System**

* **Debuff Stack Counter:**  
  * Increments once per lifecycle tick **per active negative flag**.  
* **Debuff flags:**  
  * filthy\_debuff: float  
  * hungry\_debuff: float  
  * overfed\_debuff: float  
  * starving\_debuff: float  
  * dirty\_debuff: float  
  * lonely\_debuff: float  
  * abandoned\_debuff: float  
* **Lifespan Reduction:**  
  * Each negative flag reduces the max lifespan by a fixed amount per flag.  
* **Effect Preview (optional):**  
  * UI can show the impact on remaining lifespan.  
* Max lifespan: 80 yrs