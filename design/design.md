# Design for Z HMC OS Message Forwarder

## Functionality

* Runs as a process that gets OS messages from certain partitions and sends them
  to a remote syslog service.

* One forwarder process connects to one HMC and handles all of its managed CPCs.

* The CPCs can be in classic mode (then the messages are from OSs in LPARs) or
  in DPM mode (then the messages are from OSs in partitions).

* The LPARs and partitions are selected by CPC name and LPAR/partition name,
  whereby these names can be specified as a list whose items are regular
  expressions.

* On CPCs in DPM mode, newly created partitions that match the specified names
  are automatically started to be forwarded.

* On CPCs in DPM mode, partitions that have been forwarded and that are being
  deleted, are automatically stopped to be forwarded.

* TBD: New CPCs and CPCs that go away are also automatically handled.

* HMC reboots are automatically recovered.

* A forwarder config change requires the forwarder to be restarted.

* Restarts of the forwarder process automatically detect the last OS message
  from each LPAR/partition and resume the forwarding at the right point,
  so that there are no duplicates and no gaps in what is sent to the syslog
  service.

## General approach

The forwarder will read a config file which provides access data for the HMC,
and a definition of CPCs and LPARs/Partitions for which the forwarding should
be done.

It retrieves the zhmcclient.LPAR/Partition objects for the matching partitions
from the matching CPCs, and opens an OS message channel for those that are active.
Inactive partitions should return 409.332 when opening an OS message channel.

A zhmcclient.NotificationReceiver is started with the following topics:
- the inventory change topic (from login)
- the OS message channel topics for the initially matching LPARs/partitions.

When an inventory change notification is received:
- for creation of an LPAR/Partition, the forwarder retrieves the
  zhmcclient.LPAR/Partition object and checks for a name match. If the name
  matches, it opens the OS message channel, and adds the new topic to the
  zhmcclient.NotificationReceiver.
- for deletion of an LPAR/Partition, the forwarder checks its list of partitions
  it forwards for, and if the deleted partition is part of that, remove it
  from that list, and (TBD) also remove its OS message topic from the
  zhmcclient.NotificationReceiver.
- for adding a CPC to the managed CPCs of the HMC: TBD
- for removing a CPC from the managed CPCs of the HMC: TBD

When an OS message notification is received:
- If there is a matching LPAR/partition, check if its sequence number is older
  than the last sent message for that LPAR/partition. If not younger it is a
  duplicate and the message is dropped.
  If younger, send the messge to the syslog server, and update the last sent
  message sequence number.
- If there is no matching LPAR/partition, log that (should not happen).

## Detection of OS message sequence

In the OS message notification, the HMC provides the
"sequence-number" field. These are consecutive numbers for each LPAR/partition,
and that provides for the detection of duplicates or gaps.

The information about the last sent sequence number is stored in a file.
There is one file per forwarder process, so that running multiple forwarders
with overlapping partitions can be supported.
