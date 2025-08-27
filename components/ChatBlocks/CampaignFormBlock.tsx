import React, { useState } from 'react';

interface CampaignFormField {
  name: string;
  label: string;
  type: string;
  required: boolean;
  placeholder?: string;
  step?: string;
  min?: string;
  options?: Array<{ value: string; label: string }>;
  default?: string;
}

interface CampaignFormBlockProps {
  title: string;
  description: string;
  fields: CampaignFormField[];
  onSubmit?: (formData: Record<string, any>) => void;
}

const CampaignFormBlock: React.FC<CampaignFormBlockProps> = ({ 
  title, 
  description, 
  fields, 
  onSubmit 
}) => {
  const [formData, setFormData] = useState<Record<string, any>>(() => {
    // Initialize form data with defaults
    const initial: Record<string, any> = {};
    fields.forEach(field => {
      if (field.default) {
        initial[field.name] = field.default;
      } else if (field.type === 'number') {
        initial[field.name] = '';
      } else {
        initial[field.name] = '';
      }
    });
    return initial;
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    
    fields.forEach(field => {
      if (field.required) {
        const value = formData[field.name];
        if (!value || (typeof value === 'string' && value.trim() === '')) {
          newErrors[field.name] = `${field.label} is required`;
        }
      }
      
      if (field.type === 'number' && formData[field.name]) {
        const numValue = parseFloat(formData[field.name]);
        if (isNaN(numValue) || numValue <= 0) {
          newErrors[field.name] = `${field.label} must be a positive number`;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      if (onSubmit) {
        await onSubmit(formData);
      } else {
        // Default behavior: send to chat API
        const response = await fetch('/api/chat/message/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            message: `Create campaign with name: ${formData.name}, budget: $${formData.budget_amount_micros}, type: ${formData.channel_type}, status: ${formData.status}`,
            session_id: localStorage.getItem('currentSessionId'),
            campaign_data: formData
          }),
        });

        const result = await response.json();
        if (result.success) {
          console.log('Campaign creation initiated:', result);
        } else {
          console.error('Failed to create campaign:', result.error);
        }
      }
    } catch (error) {
      console.error('Error submitting form:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (fieldName: string, value: any) => {
    setFormData(prev => ({ ...prev, [fieldName]: value }));
    
    // Clear error when user starts typing
    if (errors[fieldName]) {
      setErrors(prev => ({ ...prev, [fieldName]: '' }));
    }
  };

  const renderField = (field: CampaignFormField) => {
    const fieldId = `field-${field.name}`;
    const hasError = errors[field.name];
    
    switch (field.type) {
      case 'text':
        return (
          <input
            id={fieldId}
            type="text"
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              hasError ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        );
        
      case 'number':
        return (
          <input
            id={fieldId}
            type="number"
            step={field.step || "0.01"}
            min={field.min || "0"}
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              hasError ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        );
        
      case 'select':
        return (
          <select
            id={fieldId}
            value={formData[field.name] || field.default || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              hasError ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            {field.options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
        
      default:
        return (
          <input
            id={fieldId}
            type="text"
            value={formData[field.name] || ''}
            onChange={(e) => handleInputChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              hasError ? 'border-red-500' : 'border-gray-300'
            }`}
          />
        );
    }
  };

  return (
    <div className="bg-white rounded-lg border p-6 max-w-md">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">{title}</h3>
        <p className="text-sm text-gray-600">{description}</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {fields.map((field) => (
          <div key={field.name}>
            <label 
              htmlFor={`field-${field.name}`}
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            
            {renderField(field)}
            
            {errors[field.name] && (
              <p className="text-red-500 text-sm mt-1">{errors[field.name]}</p>
            )}
          </div>
        ))}

        <div className="pt-4">
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Creating Campaign...' : 'Create Campaign'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CampaignFormBlock;
