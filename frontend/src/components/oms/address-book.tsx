'use client';

import { type FormEvent, useEffect, useMemo, useState } from 'react';
import { Home, MapPin, Plus, Save, Trash2 } from 'lucide-react';

import {
  useOmsAddresses,
  useOmsArchiveAddress,
  useOmsCreateAddress,
  useOmsUpdateAddress,
} from '@/hooks';
import type { AddressRequest } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

const emptyForm: AddressRequest = {
  label: 'home',
  custom_label: '',
  line1: '',
  line2: '',
  city: '',
  state: '',
  postal_code: '',
  country: 'NP',
  phone: '',
  is_default: false,
};

export function AddressBook() {
  const { data: addresses = [], isLoading } = useOmsAddresses();
  const createAddress = useOmsCreateAddress();
  const updateAddress = useOmsUpdateAddress();
  const archiveAddress = useOmsArchiveAddress();

  const [editingId, setEditingId] = useState<number | null>(null);
  const [form, setForm] = useState<AddressRequest>(emptyForm);
  const [message, setMessage] = useState<{ tone: 'success' | 'error'; text: string } | null>(null);

  const editingAddress = useMemo(
    () => addresses.find((address) => address.id === editingId) ?? null,
    [addresses, editingId]
  );

  useEffect(() => {
    if (!editingAddress) {
      setForm(emptyForm);
      return;
    }

    setForm({
      label: editingAddress.label,
      custom_label: editingAddress.custom_label,
      line1: editingAddress.line1,
      line2: editingAddress.line2,
      city: editingAddress.city,
      state: editingAddress.state,
      postal_code: editingAddress.postal_code,
      country: editingAddress.country,
      phone: editingAddress.phone,
      is_default: editingAddress.is_default,
    });
  }, [editingAddress]);

  const resetForm = () => {
    setEditingId(null);
    setForm(emptyForm);
  };

  const validate = () => {
    if (!form.line1.trim() || !form.city.trim() || !form.postal_code.trim()) {
      setMessage({ tone: 'error', text: 'Line 1, city, and postal code are required.' });
      return false;
    }
    return true;
  };

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage(null);
    if (!validate()) return;

    try {
      if (editingId) {
        await updateAddress.mutateAsync({ addressId: editingId, payload: form });
        setMessage({ tone: 'success', text: 'Address updated.' });
      } else {
        await createAddress.mutateAsync(form);
        setMessage({ tone: 'success', text: 'Address added.' });
      }
      resetForm();
    } catch {
      setMessage({ tone: 'error', text: 'We could not save this address. Please try again.' });
    }
  };

  const onArchive = async (addressId: number) => {
    setMessage(null);
    try {
      await archiveAddress.mutateAsync(addressId);
      if (editingId === addressId) {
        resetForm();
      }
      setMessage({ tone: 'success', text: 'Address archived.' });
    } catch {
      setMessage({ tone: 'error', text: 'This address could not be removed.' });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-xl">
          <MapPin className="h-5 w-5" />
          Delivery Addresses
        </CardTitle>
        <CardDescription>
          Save serviceable delivery locations for faster sushi orders and easier checkout.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {message && (
          <div
            className={`rounded-lg px-4 py-3 text-sm ${
              message.tone === 'success'
                ? 'bg-emerald-50 text-emerald-700'
                : 'bg-red-50 text-red-700'
            }`}
          >
            {message.text}
          </div>
        )}

        <div className="grid gap-4">
          {isLoading && <div className="text-sm text-gray-500">Loading addresses...</div>}
          {!isLoading && addresses.length === 0 && (
            <div className="rounded-lg border border-dashed border-gray-300 p-4 text-sm text-gray-500">
              No saved delivery addresses yet.
            </div>
          )}
          {addresses.map((address) => (
            <div
              key={address.id}
              className="rounded-xl border border-gray-200 p-4 shadow-[0_1px_2px_rgba(15,23,42,0.04)]"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-orange-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-orange-700">
                      {address.label === 'custom' ? address.custom_label || 'Custom' : address.label}
                    </span>
                    {address.is_default && (
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-700">
                        Default
                      </span>
                    )}
                    <span
                      className={`rounded-full px-2.5 py-1 text-xs font-medium ${
                        address.is_serviceable
                          ? 'bg-emerald-100 text-emerald-700'
                          : 'bg-amber-100 text-amber-700'
                      }`}
                    >
                      {address.is_serviceable ? 'Serviceable' : 'Outside current zone'}
                    </span>
                  </div>
                  <div className="text-sm text-slate-700">
                    <p>{address.line1}</p>
                    {address.line2 && <p>{address.line2}</p>}
                    <p>
                      {address.city}
                      {address.state ? `, ${address.state}` : ''} {address.postal_code}
                    </p>
                    <p>{address.phone || 'No phone added'}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button type="button" variant="outline" size="sm" onClick={() => setEditingId(address.id)}>
                    Edit
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => onArchive(address.id)}
                    disabled={archiveAddress.isPending}
                  >
                    <Trash2 className="mr-1 h-4 w-4" />
                    Remove
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <form onSubmit={onSubmit} className="space-y-4 rounded-xl border border-gray-200 bg-gray-50/70 p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h3 className="text-lg font-semibold text-slate-900">
                {editingId ? 'Update Delivery Address' : 'Add Delivery Address'}
              </h3>
              <p className="text-sm text-gray-500">
                Keep default and serviceable delivery details ready for checkout.
              </p>
            </div>
            {editingId ? (
              <Button type="button" variant="ghost" size="sm" onClick={resetForm}>
                Cancel
              </Button>
            ) : (
              <Home className="h-5 w-5 text-orange-500" />
            )}
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-gray-700" htmlFor="label">
                Label
              </label>
              <select
                id="label"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={form.label}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    label: event.target.value as AddressRequest['label'],
                  }))
                }
              >
                <option value="home">Home</option>
                <option value="work">Work</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <Input
              id="custom_label"
              label="Custom Label"
              placeholder="Apartment, Office, Friend"
              value={form.custom_label}
              onChange={(event) => setForm((current) => ({ ...current, custom_label: event.target.value }))}
              disabled={form.label !== 'custom'}
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Input
              id="line1"
              label="Address Line 1"
              placeholder="Street, building, landmark"
              value={form.line1}
              onChange={(event) => setForm((current) => ({ ...current, line1: event.target.value }))}
            />
            <Input
              id="line2"
              label="Address Line 2"
              placeholder="Apartment, floor, notes"
              value={form.line2}
              onChange={(event) => setForm((current) => ({ ...current, line2: event.target.value }))}
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Input
              id="city"
              label="City"
              value={form.city}
              onChange={(event) => setForm((current) => ({ ...current, city: event.target.value }))}
            />
            <Input
              id="state"
              label="State"
              value={form.state}
              onChange={(event) => setForm((current) => ({ ...current, state: event.target.value }))}
            />
            <Input
              id="postal_code"
              label="Postal Code"
              value={form.postal_code}
              onChange={(event) => setForm((current) => ({ ...current, postal_code: event.target.value }))}
            />
            <Input
              id="country"
              label="Country"
              value={form.country}
              onChange={(event) => setForm((current) => ({ ...current, country: event.target.value }))}
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Input
              id="phone"
              label="Phone"
              placeholder="+977..."
              value={form.phone}
              onChange={(event) => setForm((current) => ({ ...current, phone: event.target.value }))}
            />
            <label className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm text-gray-700">
              <input
                type="checkbox"
                checked={form.is_default}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    is_default: event.target.checked,
                  }))
                }
              />
              Set as default delivery address
            </label>
          </div>

          <Button
            type="submit"
            isLoading={createAddress.isPending || updateAddress.isPending}
            className="bg-orange-600 hover:bg-orange-700 focus:ring-orange-500"
          >
            {editingId ? (
              <>
                <Save className="mr-2 h-4 w-4" />
                Save Address
              </>
            ) : (
              <>
                <Plus className="mr-2 h-4 w-4" />
                Add Address
              </>
            )}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
