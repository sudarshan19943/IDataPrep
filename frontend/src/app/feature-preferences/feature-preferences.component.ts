import { Component, OnInit, EventEmitter, Output } from '@angular/core';
import {sent, received} from './Features'
import { MatChipInputEvent } from '@angular/material/chips';
import {COMMA, ENTER} from '@angular/cdk/keycodes';

@Component({
  selector: 'app-feature-preferences',
  templateUrl: './feature-preferences.component.html',
  styleUrls: ['./feature-preferences.component.scss']
})
export class FeaturePreferencesComponent implements OnInit {

  @Output() completed = new EventEmitter<boolean>();
  readonly separatorKeysCodes: number[] = [ENTER, COMMA];
  FeatureType = {'t1': 'numeric', 't2': 'categorical'};
  featuresReceived;

  constructor() { }

  ngOnInit() {
    this.onFeaturesReceived(received);
    console.log(this.featuresReceived);
  }

  onFeaturesReceived(_received: any) {
    _received.forEach(feature => {
      feature.preferences = feature.preferences ? feature.preferences : {};
      feature.preferences.zeroAllowed = feature.preferences.zeroAllowed === undefined ? false : feature.preferences.zeroAllowed;
      feature.preferences.negativeAllowed = feature.preferences.negativeAllowed === undefined ? false : feature.preferences.negativeAllowed;
      feature.preferences.categories = feature.preferences.categories === undefined ? [] : feature.preferences.categories;
    });
    this.featuresReceived = _received;
  }

  addCategory(featureIndex: any, event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;

    if ((value || '').trim()) {
      this.featuresReceived[featureIndex].preferences.categories.push(value.trim());
    }

    if (input) {
      input.value = '';
    }
    console.log(this.featuresReceived[featureIndex].preferences.categories);
  }

  removeCategory(featureIndex: any, category: String): void {
    const index = this.featuresReceived[featureIndex].preferences.categories.indexOf(category);

    if (index >= 0) {
      this.featuresReceived[featureIndex].preferences.categories.splice(index, 1);
    }
    console.log(this.featuresReceived[featureIndex].preferences.categories);

  }

  onZeroAllowedChange(featureIndex, event: any) {
    this.featuresReceived[featureIndex].preferences.zeroAllowed = event.checked;
  }

  onNegAllowedChange(featureIndex, event: any) {
    this.featuresReceived[featureIndex].preferences.negativeAllowed = event.checked;
  }

  onFeatureNameInput(featureIndex, event: any) {
    this.featuresReceived[featureIndex].name = event.target.value;
  }

  saveAndStartProcessing() {
    this.featuresReceived.forEach(feature => {
      if (feature.type === this.FeatureType.t1) {
        delete feature.preferences.categories;
      } else if (feature.type === this.FeatureType.t2) {
        delete feature.preferences.negativeAllowed;
        delete feature.preferences.zeroAllowed;
      }
    });
    console.log(this.featuresReceived);
    this.completed.emit(true);
  }

}
