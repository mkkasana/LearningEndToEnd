import { describe, expect, it } from "vitest"
import type { PersonSearchResult } from "@/client"
import type {
  AddressFormData,
  BasicInfoFormData,
  PersonSearchCriteria,
  ReligionFormData,
  SelectedPerson,
} from "../types"
import {
  buildSearchRequest,
  calculateTotalPages,
  extractBirthYear,
  formatPersonName,
  formatSelectedPersonDisplay,
  isValidAddress,
  isValidBasicInfo,
  isValidReligion,
  toSelectedPerson,
} from "./searchUtils"

describe("searchUtils - extractBirthYear", () => {
  it("should return null for null input", () => {
    expect(extractBirthYear(null)).toBeNull()
  })

  it("should return null for undefined input", () => {
    expect(extractBirthYear(undefined)).toBeNull()
  })

  it("should return null for empty string", () => {
    expect(extractBirthYear("")).toBeNull()
  })

  it("should extract year from ISO date string", () => {
    expect(extractBirthYear("1990-05-15")).toBe(1990)
    expect(extractBirthYear("2000-06-15")).toBe(2000)
    expect(extractBirthYear("1985-07-15")).toBe(1985)
  })

  it("should extract year from full ISO datetime string", () => {
    expect(extractBirthYear("1990-05-15T10:30:00Z")).toBe(1990)
  })

  it("should return null for invalid date string", () => {
    expect(extractBirthYear("invalid-date")).toBeNull()
  })
})

describe("searchUtils - formatPersonName", () => {
  it("should format name with first and last name only", () => {
    const person = { first_name: "John", middle_name: null, last_name: "Doe" }
    expect(formatPersonName(person)).toBe("John Doe")
  })

  it("should format name with middle name", () => {
    const person = {
      first_name: "John",
      middle_name: "William",
      last_name: "Doe",
    }
    expect(formatPersonName(person)).toBe("John William Doe")
  })

  it("should handle empty middle name", () => {
    const person = { first_name: "Jane", middle_name: "", last_name: "Smith" }
    expect(formatPersonName(person)).toBe("Jane Smith")
  })

  it("should handle undefined middle name", () => {
    const person = {
      first_name: "Jane",
      middle_name: undefined,
      last_name: "Smith",
    }
    expect(formatPersonName(person)).toBe("Jane Smith")
  })
})

describe("searchUtils - toSelectedPerson", () => {
  it("should transform PersonSearchResult to SelectedPerson", () => {
    const searchResult: PersonSearchResult = {
      person_id: "uuid-123",
      first_name: "John",
      middle_name: null,
      last_name: "Doe",
      date_of_birth: "1990-05-15",
      name_match_score: 85,
    }

    const result = toSelectedPerson(searchResult)

    expect(result).toEqual({
      personId: "uuid-123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
    })
  })

  it("should handle null date_of_birth", () => {
    const searchResult: PersonSearchResult = {
      person_id: "uuid-456",
      first_name: "Jane",
      middle_name: "Marie",
      last_name: "Smith",
      date_of_birth: "",
      name_match_score: 75,
    }

    const result = toSelectedPerson(searchResult)

    expect(result).toEqual({
      personId: "uuid-456",
      firstName: "Jane",
      lastName: "Smith",
      birthYear: null,
    })
  })
})

describe("searchUtils - calculateTotalPages", () => {
  it("should return 0 for 0 total items", () => {
    expect(calculateTotalPages(0, 20)).toBe(0)
  })

  it("should return 0 for negative total", () => {
    expect(calculateTotalPages(-5, 20)).toBe(0)
  })

  it("should return 0 for 0 page size", () => {
    expect(calculateTotalPages(100, 0)).toBe(0)
  })

  it("should return 1 for items less than page size", () => {
    expect(calculateTotalPages(15, 20)).toBe(1)
  })

  it("should return 1 for items equal to page size", () => {
    expect(calculateTotalPages(20, 20)).toBe(1)
  })

  it("should return correct pages for items greater than page size", () => {
    expect(calculateTotalPages(21, 20)).toBe(2)
    expect(calculateTotalPages(40, 20)).toBe(2)
    expect(calculateTotalPages(41, 20)).toBe(3)
    expect(calculateTotalPages(100, 20)).toBe(5)
  })
})

describe("searchUtils - isValidBasicInfo", () => {
  it("should return true for valid basic info", () => {
    const data: BasicInfoFormData = {
      firstName: "John",
      lastName: "Doe",
    }
    expect(isValidBasicInfo(data)).toBe(true)
  })

  it("should return true with optional fields", () => {
    const data: BasicInfoFormData = {
      firstName: "John",
      lastName: "Doe",
      genderId: "male-uuid",
      birthYearFrom: 1980,
      birthYearTo: 1990,
    }
    expect(isValidBasicInfo(data)).toBe(true)
  })

  it("should return false for empty first name", () => {
    const data: BasicInfoFormData = {
      firstName: "",
      lastName: "Doe",
    }
    expect(isValidBasicInfo(data)).toBe(false)
  })

  it("should return false for whitespace-only first name", () => {
    const data: BasicInfoFormData = {
      firstName: "   ",
      lastName: "Doe",
    }
    expect(isValidBasicInfo(data)).toBe(false)
  })

  it("should return false for empty last name", () => {
    const data: BasicInfoFormData = {
      firstName: "John",
      lastName: "",
    }
    expect(isValidBasicInfo(data)).toBe(false)
  })

  it("should return false for whitespace-only last name", () => {
    const data: BasicInfoFormData = {
      firstName: "John",
      lastName: "   ",
    }
    expect(isValidBasicInfo(data)).toBe(false)
  })
})

describe("searchUtils - isValidAddress", () => {
  it("should return true for valid address with required fields", () => {
    const data: AddressFormData = {
      countryId: "country-uuid",
      stateId: "state-uuid",
      districtId: "district-uuid",
    }
    expect(isValidAddress(data)).toBe(true)
  })

  it("should return true with optional fields", () => {
    const data: AddressFormData = {
      countryId: "country-uuid",
      stateId: "state-uuid",
      districtId: "district-uuid",
      subDistrictId: "sub-district-uuid",
      localityId: "locality-uuid",
    }
    expect(isValidAddress(data)).toBe(true)
  })

  it("should return false for empty countryId", () => {
    const data: AddressFormData = {
      countryId: "",
      stateId: "state-uuid",
      districtId: "district-uuid",
    }
    expect(isValidAddress(data)).toBe(false)
  })

  it("should return false for empty stateId", () => {
    const data: AddressFormData = {
      countryId: "country-uuid",
      stateId: "",
      districtId: "district-uuid",
    }
    expect(isValidAddress(data)).toBe(false)
  })

  it("should return false for empty districtId", () => {
    const data: AddressFormData = {
      countryId: "country-uuid",
      stateId: "state-uuid",
      districtId: "",
    }
    expect(isValidAddress(data)).toBe(false)
  })
})

describe("searchUtils - isValidReligion", () => {
  it("should return true for valid religion with required fields", () => {
    const data: ReligionFormData = {
      religionId: "religion-uuid",
      religionCategoryId: "category-uuid",
    }
    expect(isValidReligion(data)).toBe(true)
  })

  it("should return true with optional sub-category", () => {
    const data: ReligionFormData = {
      religionId: "religion-uuid",
      religionCategoryId: "category-uuid",
      religionSubCategoryId: "sub-category-uuid",
    }
    expect(isValidReligion(data)).toBe(true)
  })

  it("should return false for empty religionId", () => {
    const data: ReligionFormData = {
      religionId: "",
      religionCategoryId: "category-uuid",
    }
    expect(isValidReligion(data)).toBe(false)
  })

  it("should return false for empty religionCategoryId", () => {
    const data: ReligionFormData = {
      religionId: "religion-uuid",
      religionCategoryId: "",
    }
    expect(isValidReligion(data)).toBe(false)
  })
})

describe("searchUtils - formatSelectedPersonDisplay", () => {
  it("should format person with birth year", () => {
    const person: SelectedPerson = {
      personId: "uuid-123",
      firstName: "John",
      lastName: "Doe",
      birthYear: 1990,
    }
    expect(formatSelectedPersonDisplay(person)).toBe("John Doe (1990)")
  })

  it("should format person without birth year", () => {
    const person: SelectedPerson = {
      personId: "uuid-456",
      firstName: "Jane",
      lastName: "Smith",
      birthYear: null,
    }
    expect(formatSelectedPersonDisplay(person)).toBe("Jane Smith")
  })
})

describe("searchUtils - buildSearchRequest", () => {
  const createBasicCriteria = (): PersonSearchCriteria => ({
    basicInfo: {
      firstName: "John",
      lastName: "Doe",
    },
    address: {
      countryId: "country-uuid",
      stateId: "state-uuid",
      districtId: "district-uuid",
    },
    religion: {
      religionId: "religion-uuid",
      religionCategoryId: "category-uuid",
    },
  })

  it("should build request with required fields only", () => {
    const criteria = createBasicCriteria()
    const result = buildSearchRequest(criteria)

    expect(result).toEqual({
      first_name: "John",
      last_name: "Doe",
      gender_id: undefined,
      birth_year_from: undefined,
      birth_year_to: undefined,
      country_id: "country-uuid",
      state_id: "state-uuid",
      district_id: "district-uuid",
      sub_district_id: "",
      locality_id: undefined,
      religion_id: "religion-uuid",
      religion_category_id: "category-uuid",
      religion_sub_category_id: undefined,
      skip: 0,
      limit: 20,
    })
  })

  it("should build request with all optional fields", () => {
    const criteria: PersonSearchCriteria = {
      basicInfo: {
        firstName: "John",
        lastName: "Doe",
        genderId: "male-uuid",
        birthYearFrom: 1980,
        birthYearTo: 1990,
      },
      address: {
        countryId: "country-uuid",
        stateId: "state-uuid",
        districtId: "district-uuid",
        subDistrictId: "sub-district-uuid",
        localityId: "locality-uuid",
      },
      religion: {
        religionId: "religion-uuid",
        religionCategoryId: "category-uuid",
        religionSubCategoryId: "sub-category-uuid",
      },
    }

    const result = buildSearchRequest(criteria)

    expect(result).toEqual({
      first_name: "John",
      last_name: "Doe",
      gender_id: "male-uuid",
      birth_year_from: 1980,
      birth_year_to: 1990,
      country_id: "country-uuid",
      state_id: "state-uuid",
      district_id: "district-uuid",
      sub_district_id: "sub-district-uuid",
      locality_id: "locality-uuid",
      religion_id: "religion-uuid",
      religion_category_id: "category-uuid",
      religion_sub_category_id: "sub-category-uuid",
      skip: 0,
      limit: 20,
    })
  })

  it("should use custom skip and limit values", () => {
    const criteria = createBasicCriteria()
    const result = buildSearchRequest(criteria, 40, 10)

    expect(result.skip).toBe(40)
    expect(result.limit).toBe(10)
  })

  it("should handle empty optional string fields", () => {
    const criteria: PersonSearchCriteria = {
      basicInfo: {
        firstName: "",
        lastName: "",
        genderId: "",
      },
      address: {
        countryId: "country-uuid",
        stateId: "state-uuid",
        districtId: "district-uuid",
        subDistrictId: "",
        localityId: "",
      },
      religion: {
        religionId: "religion-uuid",
        religionCategoryId: "category-uuid",
        religionSubCategoryId: "",
      },
    }

    const result = buildSearchRequest(criteria)

    // Empty strings should become undefined for optional fields
    expect(result.first_name).toBeUndefined()
    expect(result.last_name).toBeUndefined()
    expect(result.gender_id).toBeUndefined()
    expect(result.sub_district_id).toBe("")
    expect(result.locality_id).toBeUndefined()
    expect(result.religion_sub_category_id).toBeUndefined()
  })
})
