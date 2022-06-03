using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

struct State {
    public State(float _fractionalPosition, LineController _lineOccupied, int _direction){
        fractionalPosition = _fractionalPosition;
        lineOccupied = _lineOccupied;
        direction = _direction;
    }

    public float fractionalPosition;
    public LineController lineOccupied;
    public int direction;
}

public class CarriageNode : MonoBehaviour
{
    private LineController lineOccupied;
    private float fractionalPosition;
    private int direction;
    private bool isEndsNode;

    private State previousState;

    private CarriageNode toFollow; // Temporary

    public void Setup(LineController lineOccupied, float fractionalPosition, CarriageNode tf){
        this.lineOccupied = lineOccupied;
        this.fractionalPosition = fractionalPosition;
        this.direction = 1; // 1 if the node is traversing segment start -> finish, else -1 or 0
        this.isEndsNode = false;
        this.toFollow = tf; // Temporary
    }

    void SaveState(){
        previousState = new State(fractionalPosition, lineOccupied, direction);
    }

    void UndoStep(){
        fractionalPosition = previousState.fractionalPosition;
        lineOccupied       = previousState.lineOccupied;
        direction          = previousState.direction;
    }

    int Step(float velocity, bool save=false){
        // Move forward a fixed distance. Returns True on any movement. //
        // Error codes: 0 - success, 1 - failure //
        if (save){ SaveState(); }

        velocity *= direction; // The velocity in the direction in which the train is treating this segment of track
        float lineLength = lineOccupied.length;
        float fractionalChange = velocity / lineLength;
        float newFractionalPosition = fractionalPosition + fractionalChange;
        JunctionController junction;
        float overshoot;

        if (newFractionalPosition >= 0 && newFractionalPosition <= 1){
            // Staying on same line
            fractionalPosition = newFractionalPosition;
            return 0;
        }else {
            if (newFractionalPosition < 0){
                junction = lineOccupied.startJunction;
                overshoot = 0 - newFractionalPosition;
            }else {
                junction = lineOccupied.endJunction;
                overshoot = newFractionalPosition - 1;
            }
        }

        // Switch onto new track:
        if ( !(junction is TriPointsController)){
            Debug.Log("Hit unhandled junction type, stopping. Junction type is: ");
            Debug.Log(junction);
            return 1; // Unhandled junction type, train terminates
        }

        //TriPointsController junction = (TriPointsController) junction;

        LineController nextline = ((TriPointsController) junction).nextLine(lineOccupied);
        Debug.Log("Nextline is: "+nextline);
        if (nextline == null){ // Train can't go this way!
            return 1;
        }

        Debug.Log("Node at "+ this +" steps over junction"+ junction +".");
        if (isEndsNode){
            junction.ToggleOccupied();
        }
        overshoot *= lineLength; // Gives overshoot as an absolute distance
        float fractionalOvershoot = overshoot / nextline.length; // Overshoot as a fraction of the new line

        bool nextlineStartsHere = (nextline.startJunction == junction);
        bool thislineStartsHere = (lineOccupied.startJunction == junction);

        if (nextlineStartsHere){
            // Python code sets previous fracitonalPosition to 0 here.
            fractionalPosition = 0 + fractionalOvershoot;
        }else {
            // Python code sets previous fracitonalPosition to 1 here.
            fractionalPosition = 1 - fractionalOvershoot;
        }

        // If tracks are either nose-nose or tail-tail: flip direction; otherwise, do nothing:
        if ( !(nextlineStartsHere ^ thislineStartsHere) ){
            direction *= -1;
        }

        lineOccupied = nextline;
        return 0;
    }

    int Follow(CarriageNode aheadCarriageNode, int carriageLength, float trainVelocity) {
        // Error codes: 0 - success, 1 - failure
        float relativeTrainVelocity = trainVelocity; // Initial value, independent of direction
        trainVelocity *= direction; // The velocity in the direction in which the train is treating this segment of track (absolute velocity on segment)
        // Find all points which are a carriage length away from aheadCarriageNode on this line
        List<float> intersections = lineOccupied.IntersectsCircle(aheadCarriageNode.GetPosition(), carriageLength);

        if (trainVelocity == 0){
            return 0;
        }

        // Filter out positions "behind" the current position, or ahead of ahead_carriage_node
        List<float> candidatePositions = new List<float>();
        for (int i=0; i<intersections.Count; i++){
            float intersection = intersections[i];
            // Check intersection is ahead of current position
            if (aheadOf(intersection, fractionalPosition, trainVelocity)){
                if (lineOccupied == aheadCarriageNode.lineOccupied){
                    // Then the next step must be behind ahead_carriage_node
                    if (! aheadOf(intersection, aheadCarriageNode.fractionalPosition,trainVelocity)){
                        candidatePositions.Add(intersection);
                    }
                } else {
                    // Not on the same lines, so relative fractionalPositions don't matter
                    candidatePositions.Add(intersection);
                }
            }
        }

        if (candidatePositions.Count == 1){
            // Only one place to move to
            fractionalPosition = candidatePositions[0];
        }else if(candidatePositions.Count == 0){
            if (lineOccupied == aheadCarriageNode.lineOccupied){
                // On same track as node in front, but nowhere to go, so can't move
                return 1;
            }else {
                // Nowhere to go on this track, but there may be somewhere on next track
                if (trainVelocity > 0){
                    // Put this node just beyond junction
                    fractionalPosition =  1.0001f;
                }else {
                    fractionalPosition = -0.0001f;
                }
                LineController initialLineOccupied = lineOccupied;
                //Step(0); // Stepping will now switch this node onto the next line
                Step(0);
                if (lineOccupied == initialLineOccupied){
                    throw new Exception("No valid position for following node at "+this);
                }else {
                    // Try following aheadCarriageNode, now this node is on the next line
                    Debug.Log("Attempting recursive follow!");
                    Follow(aheadCarriageNode, carriageLength, relativeTrainVelocity);
                }
            }
        }else {
            throw new Exception("More than 1 position available to move following node at "+ this +": "+ candidatePositions);
        }

        return 0;
    }

    private bool aheadOf(float carriageNode1, float carriageNode2, float trainVelocity) {
        if (trainVelocity > 0){
            return (carriageNode1 > carriageNode2);
        }else {
            return (carriageNode1 < carriageNode2);
        }
    }

    void MoveTo(CarriageNode aheadCarriageNode) {
        lineOccupied       = aheadCarriageNode.lineOccupied;
        fractionalPosition = aheadCarriageNode.fractionalPosition;
        direction          = aheadCarriageNode.direction;
    }

    Vector2 GetPosition() {
        // Interpolate position of node //
        return lineOccupied.InterpolatePosition(fractionalPosition);
    }

    public override string ToString() {
        // Display position of node //
        return GetPosition()+" on line "+lineOccupied;
    }

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        float x = Input.GetAxis("Horizontal");
        if (toFollow == null){
            Step(x*0.1f);
        }else {
            Follow(toFollow,2,x*0.1f);
        }
        Vector2 pos = GetPosition();
        gameObject.transform.position = new Vector3(pos.x,pos.y,1);
    }
}
