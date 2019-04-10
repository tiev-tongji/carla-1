// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

#pragma once

#include "CarSimPawn.h"

#include "Vehicle/CarlaWheeledVehicleState.h"
#include "Vehicle/VehicleControl.h"
#include "Vehicle/VehicleInputPriority.h"
#include "Vehicle/VehiclePhysicsControl.h"
#include "CarSimMovementComponent.h"

#include "CoreMinimal.h"
#include "CarlaCarSimVehicle.generated.h"

class UBoxComponent;
class UCarSimAgentComponent;

/// Base class for CARLA CarSim vehicles.
UCLASS()
class CARLA_API ACarlaCarSimVehicle : public ACarsimPawn
{
	GENERATED_BODY()

// ===========================================================================
/// @name Constructor and destructor
// ===========================================================================
/// @{
public:
	// Sets default values for this pawn's properties
	ACarlaCarSimVehicle();

/// @}
// ===========================================================================
/// @name Get functions
// ===========================================================================
/// @{
public:

	/// Vehicle control currently applied to this vehicle.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		const FVehicleControl &GetVehicleControl() const
	{
		return LastAppliedControl;
	}

	/// Transform of the vehicle. Location is shifted so it matches center of the
	/// vehicle bounds rather than the actor's location.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		FTransform GetVehicleTransform() const
	{
		return GetActorTransform();
	}

	/// Forward speed in cm/s. Might be negative if goes backwards.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		float GetVehicleForwardSpeed() const;

	/// Orientation vector of the vehicle, pointing forward.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		FVector GetVehicleOrientation() const;

	/// Active gear of the vehicle.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		int32 GetVehicleCurrentGear() const;

	/// Transform of the vehicle's bounding box relative to the vehicle.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		FTransform GetVehicleBoundingBoxTransform() const;

	/// Extent of the vehicle's bounding box.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		FVector GetVehicleBoundingBoxExtent() const;

	/// Get vehicle's bounding box component.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		UBoxComponent *GetVehicleBoundingBox() const
	{
		return VehicleBounds;
	}

	/// Get the maximum angle at which the front wheel can steer.
	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		float GetMaximumSteerAngle() const;
	
/// @}
// ===========================================================================
/// @name AI debug state
// ===========================================================================
/// @{
public:

	/// @todo This function should be private to AWheeledVehicleAIController.
	void SetAIVehicleState(ECarlaWheeledVehicleState InState)
	{
		State = InState;
	}

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		ECarlaWheeledVehicleState GetAIVehicleState() const
	{
		return State;
	}

	FVehiclePhysicsControl GetVehiclePhysicsControl();

	void ApplyVehiclePhysicsControl(const FVehiclePhysicsControl &PhysicsControl);

/// @}
// ===========================================================================
/// @name Vehicle input control
// ===========================================================================
/// @{
public:

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
		void ApplyVehicleControl(const FVehicleControl &Control, EVehicleInputPriority Priority)
	{
		if (InputControl.Priority <= Priority)
		{
			InputControl.Control = Control;
			InputControl.Priority = Priority;
		}
	}
	
	/// @todo This function should be private to AWheeledVehicleAIController.
	void FlushVehicleControl();

/// @}
// ===========================================================================
/// @name DEPRECATED Set functions
// ===========================================================================
/// @{
public:

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void SetThrottleInput(float Value);

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void SetSteeringInput(float Value);

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void SetBrakeInput(float Value);

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void SetReverse(bool Value);

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void ToggleReverse()
	{
		SetReverse(!LastAppliedControl.bReverse);
	}

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void SetHandbrakeInput(bool Value);

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void HoldHandbrake()
	{
		SetHandbrakeInput(true);
	}

	UFUNCTION(Category = "CARLA CarSim Vehicle", BlueprintCallable)
	void ReleaseHandbrake()
	{
		SetHandbrakeInput(false);
	}

private:
	UPROPERTY(Category = "AI Controller", VisibleAnywhere)
		ECarlaWheeledVehicleState State = ECarlaWheeledVehicleState::UNKNOWN;

	UPROPERTY(Category = "CARLA CarSim Vehicle", EditAnywhere)
		UBoxComponent *VehicleBounds;

	UPROPERTY(Category = "CARLA CarSim Vehicle", VisibleAnywhere)
		UCarSimAgentComponent *CarSimAgentComponent;

	struct
	{
		EVehicleInputPriority Priority = EVehicleInputPriority::INVALID;
		FVehicleControl Control;
	}
	InputControl;

	FVehicleControl LastAppliedControl;
};
