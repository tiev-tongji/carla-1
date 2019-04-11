// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

#pragma once

#include <queue>

#include "GameFramework/PlayerController.h"

#include "Traffic/TrafficLightState.h"
#include "Vehicle/VehicleControl.h"

#include "CarSimVehicleAIController.generated.h"

class ACarlaCarSimVehicle;
class URandomEngine;
class URoadMap;

/// CarSim vehicle controller with optional AI.
UCLASS()
class CARLA_API ACarSimVehicleAIController : public APlayerController
{
	GENERATED_BODY()

// ===========================================================================
/// @name Constructor and destructor
// ===========================================================================
/// @{

public:

	ACarSimVehicleAIController(const FObjectInitializer &ObjectInitializer);

	~ACarSimVehicleAIController();

/// @}
// ===========================================================================
/// @name APlayerController overrides
// ===========================================================================
/// @{

public:

	void Possess(APawn *aPawn) override;

	void UnPossess() override;

	void Tick(float DeltaTime) override;

/// @}
// ===========================================================================
/// @name Possessed vehicle
// ===========================================================================
/// @{

public:

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		bool IsPossessingAVehicle() const
	{
		return Vehicle != nullptr;
	}

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		ACarlaCarSimVehicle *GetPossessedVehicle()
	{
		return Vehicle;
	}

	const ACarlaCarSimVehicle *GetPossessedVehicle() const
	{
		return Vehicle;
	}

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		virtual bool IsPossessingThePlayer() const
	{
		return false;
	}

/// @}
// ===========================================================================
/// @name Control options
// ===========================================================================
/// @{

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		void SetStickyControl(bool bEnabled)
	{
		bControlIsSticky = bEnabled;
		UE_LOG(LogTemp, Warning, TEXT("StickyControl = %s"), bControlIsSticky ? TEXT("True") : TEXT("False"));
	}

/// @}
// ===========================================================================
/// @name Road map
// ===========================================================================
/// @{

public:

	void SetRoadMap(URoadMap *InRoadMap)
	{
		RoadMap = InRoadMap;
	}

	UFUNCTION(Category = "Road Map", BlueprintCallable)
		URoadMap *GetRoadMap()
	{
		return RoadMap;
	}

	/// @}
	// ===========================================================================
	/// @name Random engine
	// ===========================================================================
	/// @{

public:

	UFUNCTION(Category = "Random Engine", BlueprintCallable)
		URandomEngine *GetRandomEngine()
	{
		check(RandomEngine != nullptr);
		return RandomEngine;
	}

	/// @}
	// ===========================================================================
	/// @name Autopilot
	// ===========================================================================
	/// @{

public:

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		bool IsAutopilotEnabled() const
	{
		return bAutopilotEnabled;
	}

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		void SetAutopilot(bool Enable)
	{
		if (IsAutopilotEnabled() != Enable)
		{
			ConfigureAutopilot(Enable);
		}
	}

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		void ToggleAutopilot()
	{
		ConfigureAutopilot(!bAutopilotEnabled);
	}

private:

	void ConfigureAutopilot(bool Enable);

/// @}
// ===========================================================================
/// @name Traffic
// ===========================================================================
/// @{

public:

	/// Get current speed limit in km/h.
	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		float GetSpeedLimit() const
	{
		return SpeedLimit;
	}

	/// Set vehicle's speed limit in km/h.
	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		void SetSpeedLimit(float InSpeedLimit)
	{
		SpeedLimit = InSpeedLimit;
	}

	/// Get traffic light state currently affecting this vehicle.
	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		ETrafficLightState GetTrafficLightState() const
	{
		return TrafficLightState;
	}

	/// Set traffic light state currently affecting this vehicle.
	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		void SetTrafficLightState(ETrafficLightState InTrafficLightState)
	{
		TrafficLightState = InTrafficLightState;
	}

	/// Get traffic light currently affecting this vehicle.
	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		ATrafficLightBase *GetTrafficLight() const
	{
		return TrafficLight;
	}

	/// Set traffic light currently affecting this vehicle.
	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		void SetTrafficLight(ATrafficLightBase *InTrafficLight)
	{
		TrafficLight = InTrafficLight;
	}

	/// Set a fixed route to follow if autopilot is enabled.
	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		void SetFixedRoute(const TArray<FVector> &Locations, bool bOverwriteCurrent = true);

/// @}
// ===========================================================================
/// @name AI
// ===========================================================================
/// @{

	UFUNCTION(Category = "CarSim Vehicle Controller", BlueprintCallable)
		const FVehicleControl &GetAutopilotControl() const
	{
		return AutopilotControl;
	}

private:

	void TickAutopilotController();

	/// Returns steering value.
	float GoToNextTargetLocation(FVector &Direction);

	/// Returns steering value.
	float CalcStreeringValue(FVector &Direction);

	/// Returns throttle value.
	float Stop(float Speed);

	/// Returns throttle value.
	float Move(float Speed);

/// @}
// ===========================================================================
// -- Member variables -------------------------------------------------------
// ===========================================================================
/// @{

private:

	UPROPERTY()
		ACarlaCarSimVehicle *Vehicle = nullptr;

	UPROPERTY()
		URoadMap *RoadMap = nullptr;

	UPROPERTY()
		URandomEngine *RandomEngine = nullptr;

	UPROPERTY(VisibleAnywhere)
		bool bAutopilotEnabled = false;

	UPROPERTY(VisibleAnywhere)
		bool bControlIsSticky = true;

	UPROPERTY(VisibleAnywhere)
		float SpeedLimit = 30.0f;

	UPROPERTY(VisibleAnywhere)
		ETrafficLightState TrafficLightState = ETrafficLightState::Green;

	UPROPERTY(VisibleAnywhere)
		float MaximumSteerAngle = -1.0f;

	UPROPERTY()
		ATrafficLightBase *TrafficLight;

	FVehicleControl AutopilotControl;

	std::queue<FVector> TargetLocations;
};
