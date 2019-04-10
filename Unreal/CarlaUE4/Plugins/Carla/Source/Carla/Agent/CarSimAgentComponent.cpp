// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.

#include "Carla.h"
#include "CarSimAgentComponent.h"

static bool IsPlayer(const ACarlaCarSimVehicle &InVehicle)
{
	auto *Controller = Cast<AWheeledVehicleAIController>(InVehicle.GetController());
	return (Controller != nullptr) && Controller->IsPossessingThePlayer();
}

UCarSimAgentComponent::UCarSimAgentComponent(const FObjectInitializer &ObjectInitializer)
	: Super(ObjectInitializer) {}

void UCarSimAgentComponent::BeginPlay()
{
	Vehicle = Cast<ACarlaCarSimVehicle>(GetOwner());
	checkf(Vehicle != nullptr, TEXT("UCarSimAgentComponent can only be attached to ACarlaCarSimVehicle"));

	// We only want to register non-player agents.
	bRegisterAgentComponent = !IsPlayer(*Vehicle);

	Super::BeginPlay();
}
