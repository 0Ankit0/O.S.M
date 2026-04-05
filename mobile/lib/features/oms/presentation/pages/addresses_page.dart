import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/analytics/analytics_provider.dart';
import '../../../../core/error/error_handler.dart';
import '../../../../shared/widgets/app_text_field.dart';
import '../../../../shared/widgets/loading_button.dart';
import '../../data/models/oms_models.dart';
import '../providers/oms_provider.dart';

class AddressesPage extends ConsumerStatefulWidget {
  const AddressesPage({super.key});

  @override
  ConsumerState<AddressesPage> createState() => _AddressesPageState();
}

class _AddressesPageState extends ConsumerState<AddressesPage> {
  bool _submitting = false;

  void _showSnack(String message, {bool error = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: error ? Colors.red : Colors.green,
      ),
    );
  }

  Future<void> _refreshAddresses() async {
    await ref.refresh(omsAddressesProvider.future);
  }

  Future<void> _openAddressForm({OmsAddress? address}) async {
    final formKey = GlobalKey<FormState>();
    final label = ValueNotifier<String>(address?.label ?? 'home');
    final isDefault = ValueNotifier<bool>(address?.isDefault ?? false);
    final customLabelController = TextEditingController(
      text: address?.customLabel ?? '',
    );
    final line1Controller = TextEditingController(text: address?.line1 ?? '');
    final line2Controller = TextEditingController(text: address?.line2 ?? '');
    final cityController = TextEditingController(text: address?.city ?? '');
    final stateController = TextEditingController(text: address?.state ?? '');
    final postalController = TextEditingController(
      text: address?.postalCode ?? '',
    );
    final countryController = TextEditingController(
      text: address?.country ?? 'NP',
    );
    final phoneController = TextEditingController(text: address?.phone ?? '');

    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      builder: (sheetContext) {
        return Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 16,
            bottom: MediaQuery.of(sheetContext).viewInsets.bottom + 16,
          ),
          child: StatefulBuilder(
            builder: (context, setModalState) {
              return Form(
                key: formKey,
                child: SingleChildScrollView(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        address == null
                            ? 'Add delivery address'
                            : 'Update delivery address',
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Save a serviceable address for faster restaurant checkout.',
                        style: Theme.of(
                          context,
                        ).textTheme.bodySmall?.copyWith(color: Colors.grey),
                      ),
                      const SizedBox(height: 16),
                      ValueListenableBuilder<String>(
                        valueListenable: label,
                        builder: (_, currentLabel, __) {
                          return DropdownButtonFormField<String>(
                            value: currentLabel,
                            decoration: const InputDecoration(
                              labelText: 'Label',
                              prefixIcon: Icon(Icons.label_outline),
                            ),
                            items: const [
                              DropdownMenuItem(
                                value: 'home',
                                child: Text('Home'),
                              ),
                              DropdownMenuItem(
                                value: 'work',
                                child: Text('Work'),
                              ),
                              DropdownMenuItem(
                                value: 'custom',
                                child: Text('Custom'),
                              ),
                            ],
                            onChanged: (value) {
                              label.value = value ?? 'home';
                              setModalState(() {});
                            },
                          );
                        },
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: customLabelController,
                        label: 'Custom Label',
                        prefixIcon: Icons.edit_location_alt_outlined,
                        validator: (value) {
                          if (label.value == 'custom' &&
                              (value == null || value.trim().isEmpty)) {
                            return 'Enter a custom label';
                          }
                          return null;
                        },
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: line1Controller,
                        label: 'Address Line 1',
                        prefixIcon: Icons.home_work_outlined,
                        validator: (value) =>
                            value == null || value.trim().isEmpty
                            ? 'Enter address line 1'
                            : null,
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: line2Controller,
                        label: 'Address Line 2',
                        prefixIcon: Icons.apartment_outlined,
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: cityController,
                        label: 'City',
                        prefixIcon: Icons.location_city_outlined,
                        validator: (value) =>
                            value == null || value.trim().isEmpty
                            ? 'Enter city'
                            : null,
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: stateController,
                        label: 'State',
                        prefixIcon: Icons.map_outlined,
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: postalController,
                        label: 'Postal Code',
                        prefixIcon: Icons.markunread_mailbox_outlined,
                        validator: (value) =>
                            value == null || value.trim().isEmpty
                            ? 'Enter postal code'
                            : null,
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: countryController,
                        label: 'Country',
                        prefixIcon: Icons.public_outlined,
                      ),
                      const SizedBox(height: 12),
                      AppTextField(
                        controller: phoneController,
                        label: 'Phone',
                        prefixIcon: Icons.phone_outlined,
                        keyboardType: TextInputType.phone,
                      ),
                      const SizedBox(height: 8),
                      ValueListenableBuilder<bool>(
                        valueListenable: isDefault,
                        builder: (_, current, __) {
                          return SwitchListTile(
                            contentPadding: EdgeInsets.zero,
                            title: const Text(
                              'Set as default delivery address',
                            ),
                            value: current,
                            onChanged: (value) {
                              isDefault.value = value;
                              setModalState(() {});
                            },
                          );
                        },
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: LoadingButton(
                          isLoading: _submitting,
                          onPressed: () async {
                            if (!formKey.currentState!.validate()) return;
                            Navigator.of(sheetContext).pop();
                            await _saveAddress(
                              addressId: address?.id,
                              label: label.value,
                              customLabel: customLabelController.text.trim(),
                              line1: line1Controller.text.trim(),
                              line2: line2Controller.text.trim(),
                              city: cityController.text.trim(),
                              state: stateController.text.trim(),
                              postalCode: postalController.text.trim(),
                              country: countryController.text.trim(),
                              phone: phoneController.text.trim(),
                              isDefault: isDefault.value,
                            );
                          },
                          label: address == null
                              ? 'Add Address'
                              : 'Save Address',
                          icon: address == null
                              ? Icons.add_location_alt_outlined
                              : Icons.save_outlined,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  Future<void> _saveAddress({
    int? addressId,
    required String label,
    required String customLabel,
    required String line1,
    required String line2,
    required String city,
    required String state,
    required String postalCode,
    required String country,
    required String phone,
    required bool isDefault,
  }) async {
    setState(() => _submitting = true);
    try {
      final repository = ref.read(omsRepositoryProvider);
      if (addressId == null) {
        final saved = await repository.createAddress(
          label: label,
          customLabel: customLabel,
          line1: line1,
          line2: line2,
          city: city,
          state: state,
          postalCode: postalCode,
          country: country.isEmpty ? 'NP' : country,
          phone: phone,
          isDefault: isDefault,
        );
        ref
            .read(analyticsServiceProvider)
            .capture(
              'customer.address_created',
              properties: {'address_id': saved.id, 'label': saved.label},
            );
        _showSnack('Address added');
      } else {
        final saved = await repository.updateAddress(
          addressId: addressId,
          label: label,
          customLabel: customLabel,
          line1: line1,
          line2: line2,
          city: city,
          state: state,
          postalCode: postalCode,
          country: country.isEmpty ? 'NP' : country,
          phone: phone,
          isDefault: isDefault,
        );
        ref
            .read(analyticsServiceProvider)
            .capture(
              'customer.address_updated',
              properties: {'address_id': saved.id, 'label': saved.label},
            );
        _showSnack('Address updated');
      }
      await _refreshAddresses();
    } catch (e) {
      _showSnack(ErrorHandler.handle(e).message, error: true);
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  Future<void> _archiveAddress(int addressId) async {
    setState(() => _submitting = true);
    try {
      await ref.read(omsRepositoryProvider).archiveAddress(addressId);
      ref
          .read(analyticsServiceProvider)
          .capture(
            'customer.address_archived',
            properties: {'address_id': addressId},
          );
      await _refreshAddresses();
      _showSnack('Address removed');
    } catch (e) {
      _showSnack(ErrorHandler.handle(e).message, error: true);
    } finally {
      if (mounted) setState(() => _submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final addressesAsync = ref.watch(omsAddressesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Delivery Addresses')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _submitting ? null : () => _openAddressForm(),
        icon: const Icon(Icons.add_location_alt_outlined),
        label: const Text('Add Address'),
      ),
      body: RefreshIndicator(
        onRefresh: _refreshAddresses,
        child: addressesAsync.when(
          data: (addresses) {
            if (addresses.isEmpty) {
              return ListView(
                padding: const EdgeInsets.all(24),
                children: const [
                  SizedBox(height: 120),
                  Icon(Icons.map_outlined, size: 48, color: Colors.grey),
                  SizedBox(height: 12),
                  Center(
                    child: Text(
                      'No delivery addresses saved yet.',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                  SizedBox(height: 8),
                  Center(
                    child: Text(
                      'Add a serviceable address to speed up checkout.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                ],
              );
            }

            return ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: addresses.length,
              separatorBuilder: (_, __) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final address = addresses[index];
                final labelText =
                    address.label == 'custom' &&
                        address.customLabel.trim().isNotEmpty
                    ? address.customLabel
                    : address.label;
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 10,
                                vertical: 6,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.orange.withValues(alpha: 0.12),
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: Text(
                                labelText.toUpperCase(),
                                style: const TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.deepOrange,
                                  letterSpacing: 0.6,
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            if (address.isDefault)
                              const Chip(label: Text('Default')),
                            const Spacer(),
                            if (address.isServiceable)
                              const Chip(
                                label: Text('Serviceable'),
                                backgroundColor: Color(0xFFE8F5E9),
                              )
                            else
                              const Chip(
                                label: Text('Outside zone'),
                                backgroundColor: Color(0xFFFFF3E0),
                              ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          address.line1,
                          style: const TextStyle(fontWeight: FontWeight.w600),
                        ),
                        if (address.line2.isNotEmpty) ...[
                          const SizedBox(height: 2),
                          Text(address.line2),
                        ],
                        const SizedBox(height: 2),
                        Text(
                          '${address.city}${address.state.isNotEmpty ? ', ${address.state}' : ''} ${address.postalCode}',
                        ),
                        if (address.phone.isNotEmpty) ...[
                          const SizedBox(height: 2),
                          Text(address.phone),
                        ],
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(
                              child: OutlinedButton.icon(
                                onPressed: _submitting
                                    ? null
                                    : () => _openAddressForm(address: address),
                                icon: const Icon(Icons.edit_outlined),
                                label: const Text('Edit'),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: TextButton.icon(
                                onPressed: _submitting
                                    ? null
                                    : () => _archiveAddress(address.id),
                                icon: const Icon(
                                  Icons.delete_outline,
                                  color: Colors.red,
                                ),
                                label: const Text(
                                  'Remove',
                                  style: TextStyle(color: Colors.red),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            );
          },
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, _) => Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Text(
                ErrorHandler.handle(error).message,
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
