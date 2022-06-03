using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Linq;

public class Train : MonoBehaviour
{
    [SerializeField] GameObject carriagePrefab;
    private float velocity = 0;
    private Carriage[] carriages;

    /*public void Train(Carriage[] carriages) {
        Setup(carriages);
    }*/

    public void Setup(LineController line, float fractionalPosition, float[] carriageLengths) {
        Carriage[] carriageArray = new Carriage[carriageLengths.Length];
        for (int i=0; i<carriageLengths.Length; i++){
            GameObject clone = Instantiate(carriagePrefab, new Vector3(0,0,0), Quaternion.identity);
            carriageArray[i] = clone.GetComponent<Carriage>();
            carriageArray[i].Setup(line, fractionalPosition, carriageLengths[i]);
        }
        InternalSetup(carriageArray);
    }

    public void InternalSetup(Carriage[] carriages) {
        this.carriages = carriages;

        carriages[0].front.isEndsNode = true;
        carriages[carriages.Length-1].back.isEndsNode = true;

        // Fully expand train
        Debug.Log("Expanding train...");
        velocity = 0.1f;

        while (true){
            // Loop while at least one following node can't move
            int code = Step();
            if (code == 0){
                break;
            }else if (code == 2){
                continue; // Normal expansion
            }else { // Case 1 or 3
                throw new Exception("Cannot fully expand train!");
            }
        }
        Debug.Log("Expanding complete.");
        velocity = 0;
    }

    private int CheckCollisions (CarriageNode carriageNode){
        // 0 - no collisions, 1 - collision
        //CarriageNodeState carriageOldPosition = carriageNode.previousState;
        return 0;
    }

    public int Step() {
        // Error Codes: 0 - success, 1 - lead node cannot move, 2 - at least one following node cannot move, 3 - collision with other train, so can't move
        if (velocity == 0){
            return 0; // Success
        }

        Carriage[] orderedCarriages;
        if (velocity > 0){
            orderedCarriages = carriages;
        } else{
            orderedCarriages = carriages.Reverse().ToArray();
        }

        // Move lead node
        Carriage carriage = orderedCarriages[0];
        CarriageNode leader   = carriage.GetLeader(velocity);
        CarriageNode follower = carriage.GetFollower(velocity);
        if (leader.Step(velocity, true) != 0){
            return 1; // Lead node cannot move
        }

        if (CheckCollisions(leader) != 0){
            // Collision has occurred
            Debug.Log("REVERTING! Back on train of length "+carriages.Length);
            leader.UndoStep();
            return 3; // Collision with other train, so can't move
        }

        // Move all remaining nodes of the train
        if (follower.Follow(leader, carriage.length, velocity) != 0) {
            return 2; // A following node cannot move
        }

        CarriageNode previousCarriageBack = follower;
        for (int i=1; i<orderedCarriages.Length; i++){
            carriage = orderedCarriages[i];
            leader   = carriage.GetLeader(velocity);
            follower = carriage.GetFollower(velocity);
            leader.MoveTo(previousCarriageBack);
            if (follower.Follow(leader, carriage.length, velocity) != 0){
                return 2; // A following node cannot move
            }
            previousCarriageBack = follower;
        }
        return 0; // Success

    }

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        float x = Input.GetAxis("Horizontal");
        velocity = x * 0.1f;
        Step();
    }
}
