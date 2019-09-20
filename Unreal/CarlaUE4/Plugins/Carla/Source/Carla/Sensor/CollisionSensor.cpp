// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#include "Carla.h"
#include "Carla/Sensor/CollisionSensor.h"

#include "Carla/Actor/ActorBlueprintFunctionLibrary.h"
#include "Carla/Actor/ActorRegistry.h"
#include "Carla/Game/CarlaEpisode.h"
#include "Carla/Game/CarlaGameInstance.h"
#include "Carla/Game/CarlaGameModeBase.h"

#include "Carla/Traffic/RoutePlanner.h"

ACollisionSensor::ACollisionSensor(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer)
{
	PrimaryActorTick.bCanEverTick = false;
}

FActorDefinition ACollisionSensor::GetSensorDefinition()
{
	return UActorBlueprintFunctionLibrary::MakeGenericSensorDefinition(
		TEXT("other"),
		TEXT("collision"));
}

void ACollisionSensor::SetOwner(AActor* NewOwner)
{
	Super::SetOwner(NewOwner);

	/// @todo Deregister previous owner if there was one.

	if (NewOwner != nullptr)
	{
		UE_LOG(LogCarla, Log, TEXT("ACollisionSensor:Set Owner Name:%s"), *NewOwner->GetName());
		NewOwner->OnActorBeginOverlap.AddDynamic(this, &ACollisionSensor::OnCollisionEvent);
	}
}
void ACollisionSensor::OnCollisionEvent(AActor* SelfActor, AActor* OtherActor)
{
	UE_LOG(LogCarla, Log, TEXT("ACollisionSensor:Collide with %s"), *OtherActor->GetName());
	// if no need to send collsion with RoutePlanner(shown on client side:Unknown),
	// add judge:&& !Cast<ARoutePlanner>(OtherActor)
	if ((SelfActor != nullptr) && (OtherActor != nullptr) && !Cast<ARoutePlanner>(OtherActor))
	{
		const auto& Episode = GetEpisode();
		GetDataStream(*this).Send(
			*this,
			Episode.SerializeActor(Episode.FindOrFakeActor(SelfActor)),
			Episode.SerializeActor(Episode.FindOrFakeActor(OtherActor)));
		// record the collision event
		if (Episode.GetRecorder()->IsEnabled())
			Episode.GetRecorder()->AddCollision(SelfActor, OtherActor);
	}
}